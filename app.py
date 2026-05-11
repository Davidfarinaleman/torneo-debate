import streamlit as st
import mysql.connector
import re

def validar_dni_nie(documento):

    documento = documento.strip().upper()
    patron_dni = r'^\d{8}[A-Z]$'
    patron_nie = r'^[XYZ]\d{7}[A-Z]$'
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    if re.match(patron_dni, documento):
        numero = int(documento[:8])
        letra = documento[-1]
        letra_correcta = letras[numero % 23]
        return letra == letra_correcta
    elif re.match(patron_nie, documento):
        equivalencias = {
            "X": "0",
            "Y": "1",
            "Z": "2"
        }
        numero_nie = (
            equivalencias[documento[0]]
            + documento[1:8]
        )
        numero = int(numero_nie)
        letra = documento[-1]
        letra_correcta = letras[numero % 23]
        return letra == letra_correcta
    return False

conexion = mysql.connector.connect(
    host=st.secrets["MYSQL_HOST"],
    port=st.secrets["MYSQL_PORT"],
    user=st.secrets["MYSQL_USER"],
    password=st.secrets["MYSQL_PASSWORD"],
    database=st.secrets["MYSQL_DATABASE"]
)

cursor = conexion.cursor()

st.image("logo.png", width=180)

st.title("Sistema de Inscripción de Torneos")

st.markdown(
    "<span style='color:red'>*</span> Campos obligatorios",
    unsafe_allow_html=True
)

st.subheader("Datos del torneo")

torneo = st.selectbox(
    "Nombre del torneo", ["Torneo 1", "Torneo 2", "Torneo 3"]
    )

categoria_torneo = st.selectbox(
    "Categoría",
    ["ESO", "Bachillerato", "Universidad"]
)

st.subheader("Datos del centro")

denominacion = st.text_input("Denominación del centro *")
domicilio = st.text_input("Dirección *")
localidad = st.text_input("Localidad *")
provincia = st.text_input("Provincia *")
codigo_postal = st.text_input("Código postal *")
telefono_centro = st.text_input("Teléfono *")
correo_centro = st.text_input("Correo electrónico *")
director = st.text_input("Director del centro *")
redes = st.text_input("Redes sociales")

st.subheader("Datos de la convocatoria")

profesor = st.text_input("Profesor preparador *")
dni_profesor = st.text_input("DNI/NIE *")
telefono_profesor = st.text_input("Teléfono del profesor *")
correo_profesor = st.text_input("Correo electrónico del profesor *")

st.subheader("Equipos participantes")
num_equipos = st.number_input(
    "Número de equipos",
    min_value=1,
    max_value=3,
    step=1
)
equipos = []
for i in range(num_equipos):
    st.markdown("---")
    st.markdown(f"## Equipo {i+1}")
    nombre_equipo = st.text_input(
        "Nombre del equipo *",
        key=f"equipo_{i}"
    )
    num_miembros = st.number_input(
        "Número de integrantes *",
        min_value=1,
        max_value=5,
        step=1,
        key=f"miembros_{i}"
    )
    miembros = []
    for j in range(num_miembros):
       st.markdown(f" Integrante {j+1}")
       nombre = st.text_input(
            "Nombre y apellidos *",
            key=f"nombre_{i}_{j}"
        )
       dni = st.text_input(
            "DNI/NIE *",
            key=f"dni_{i}_{j}"
        )
       curso = st.text_input(
            "Curso *",
            key=f"curso_{i}_{j}"
        )
       mail = st.text_input(
                "Correo electrónico",
                key=f"mail_{i}_{j}"
          )
       rol = st.selectbox(
            "Rol *",
            ["Alumno", "Capitán", "Suplente"],
            key=f"rol_{i}_{j}"
        ) 
    miembros.append({
            "numero_participante": j + 1,
            "nombre": nombre,
            "dni": dni,
            "curso": curso,
            "mail": mail,
            "rol": rol
        })
    equipos.append({
        "numero_equipo": i + 1,
        "nombre_equipo": nombre_equipo,
        "miembros": miembros
    })

if st.form_submit_button("Enviar solicitud"):
    if not denominacion.strip():
        st.error("La denominación del centro es obligatoria")
        st.stop()

    if not localidad.strip():
        st.error("La localidad es obligatoria")
        st.stop()

    if not provincia.strip():
        st.error("La provincia es obligatoria")
        st.stop()
        
    if not telefono_centro.strip():
        st.error("El teléfono del centro es obligatorio")
        st.stop()
        
    if not correo_centro.strip():
        st.error("El correo del centro es obligatorio")
        st.stop()
            
    if not director.strip():
        st.error("El director del centro es obligatorio")
        st.stop()
            
    if not profesor.strip():
        st.error("El profesor preparador es obligatorio")
        st.stop()

    if not dni_profesor.strip():
        st.error("El DNI/NIE del profesor es obligatorio")
        st.stop()

    if not validar_dni_nie(dni_profesor):
        st.error("El DNI/NIE del profesor no es válido")
        st.stop()

    if not telefono_profesor.strip():
        st.error("El teléfono del profesor es obligatorio")
        st.stop()

    if not correo_profesor.strip():
        st.error("El correo del profesor es obligatorio")
        st.stop()
    if not dni_profesor.strip():
        st.error("El DNI/NIE del profesor es obligatorio")
        st.stop()
    if not validar_dni_nie(dni_profesor):
        st.error("El DNI/NIE del profesor no es válido")
        st.stop()
        st.error("El DNI/NIE del profesor es obligatorio")
        st.stop()

    sql_torneo = """
    INSERT INTO torneos (nombre)
    VALUES (%s)
    ON DUPLICATE KEY UPDATE
    nombre = VALUES(nombre)
    """
    cursor.execute(sql_torneo, (torneo,))
    conexion.commit()
    cursor.execute("SELECT id FROM torneos WHERE nombre = %s", (torneo,))
    torneo_id = cursor.fetchone()[0]
    for equipo in equipos:
        if not equipo["nombre_equipo"].strip():
            st.error("Todos los equipos deben tener nombre")
            st.stop()
        if len(equipo["miembros"]) == 0:
            st.error(
            f"El equipo {equipo['nombre_equipo']} no tiene participantes"
        )
        st.stop()
        
        sql_centro = """
        INSERT INTO centros (
        denominacion,
        direccion,
        localidad,
        provincia,
        codigo_postal,
        telefono,
        correo,
        director,
        redes_sociales
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        direccion = VALUES(direccion),
        localidad = VALUES(localidad),
        provincia = VALUES(provincia),
        codigo_postal = VALUES(codigo_postal),
        telefono = VALUES(telefono),
        correo = VALUES(correo),
        director = VALUES(director),
        redes_sociales = VALUES(redes_sociales)
        """
        cursor.execute(sql_centro, (
            denominacion,
            direccion,
            localidad,
            provincia,
            codigo_postal,
            telefono_centro,
            correo_centro,
            director,
            redes
            ))
        conexion.commit()
        cursor.execute(
             "SELECT id FROM centros WHERE denominacion = %s",
             (denominacion,)
             )
        centro_id = cursor.fetchone()[0]
       
        sql_equipo = """
        INSERT INTO equipos (torneo_id,numero_equipo,centro, tutor, nombre_equipo, tutor_dni)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        nombre_equipo = VALUES(nombre_equipo),
        centro = VALUES(centro),
        tutor = VALUES(tutor)
        """
        cursor.execute(sql_equipo, (
            torneo_id,
            equipo["numero_equipo"],
            denominacion,
            profesor,
            equipo["nombre_equipo"],
            dni_profesor
        ))
        conexion.commit()
        cursor.execute("""
                       SELECT id
                       FROM equipos
                       WHERE torneo_id = %s
                       AND numero_equipo = %s
                       """, (torneo_id,equipo["numero_equipo"]))
        equipo_id = cursor.fetchone()[0]
        for miembro in equipo["miembros"]:
            if not miembro["nombre"].strip():
                st.error("Todos los participantes deben tener nombre")
                st.stop()
                if not miembro["dni"].strip():
                    st.error("Todos los participantes deben tener DNI/NIE")
                    st.stop()
                    if not validar_dni_nie(miembro["dni"]):
                        st.error(
                            f"El DNI/NIE de {miembro['nombre']} no es válido"
                              )
                        st.stop()
                        if not miembro["curso"].strip():
                            st.error(
                                f"El participante {miembro['nombre']} debe tener curso"
                                )
                            st.stop()
            if not miembro["dni"].strip():
                st.error("Todos los participantes deben tener DNI/NIE")
                st.stop()
            if not validar_dni_nie(miembro["dni"]):
                st.error(
                    f"El DNI/NIE de {miembro['nombre']} no es válido"
                    )
                st.stop()
            nombre_completo = miembro["nombre"].split(" ", 1)
            nombre = nombre_completo[0]
            if len(nombre_completo) > 1:
                apellidos = nombre_completo[1]
            else:
                apellidos = ""
            sql_debatiente = """
            INSERT INTO debatientes (
                equipo_id,
                numero_participante,
                nombre,
                apellidos,
                dni,
                curso,
                correo,
                rol
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            nombre = VALUES(nombre),
            apellidos = VALUES(apellidos),
            dni = VALUES(dni),
            curso = VALUES(curso),
            correo = VALUES(correo),
            rol = VALUES(rol)
            """
            valores = (
                equipo_id,
                miembro["numero_participante"],
                nombre,
                apellidos,
                miembro["dni"],
                miembro["curso"],
                miembro["mail"],
                miembro["rol"]
            )
            cursor.execute(sql_debatiente, valores)

    conexion.commit()
    cursor.close()
    conexion.close()

    st.success("Inscripción enviada correctamente")