"""
main method that contains app factory
"""
#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Autor: Rafael Amador Galván
# Fecha: 11/07/2022
import os
import sys
from pathlib import Path
import json
from datetime import datetime
from flask import Flask, render_template, url_for, session, request, redirect
from . import utils
from . import database_driver
from . import config_reader


def internal_server_error(error):
    """
    method to handle 500 HTTP errors
    """
    urls = utils.get_res_url()
    return render_template('500.html', urls=urls), 500


def not_found(error):
    """
    method to handle 404 HTTP errors
    """
    urls = utils.get_res_url()
    return render_template('404.html', urls=urls), 404


def create_app():
    """
    create and configure the Flask app
    """

    obj_ds = {}
    app = Flask(__name__, instance_relative_config=True)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(404, not_found)

    app.cli.add_command(utils.config_cli)
    app.cli.add_command(utils.database_cli)

    with app.app_context():
        # configure_app(Path(app.instance_path).joinpath('config.json').resolve(True))
        # k = Path(app.instance_path).joinpath('config.json')
        # print(k, file=sys.stdout)
        obj_ds = config_reader.configure_app(
            Path(app.instance_path).joinpath('config.json'))
        app.config.from_mapping(config_reader.parse_flask_config(obj_ds))

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/logout/')
    def logout():
        session.pop('username')
        session.pop('userid')
        session.pop('zonaname')
        session.pop('zonaid')
        session.pop('deptoname')
        session.pop('deptoid')
        return redirect(url_for('home'))

    @app.route('/login/', methods=['POST'])
    def login():
        if request.method == 'POST':
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cur = driver.connection.cursor()
            query = ("SELECT u.id_usuario, u.nombre, z.id_zona, z.nombre AS zona, "
                     "d.id_departamento, d.nombre AS departamento "
                     "FROM usuarios AS u INNER JOIN zona AS z ON(z.id_zona = u.id_zona) "
                     "INNER JOIN departamento AS d ON(d.id_departamento = u.id_departamento) "
                     "WHERE u.token=?")
            params = []
            params.append(request.form['token'])
            cur.execute(query, params)
            if cur.arraysize == 1:
                row = cur.fetchone()
                if row is None:
                    return redirect(url_for('home'))
                session['userid'] = row[0]
                session['username'] = row[1]
                session['zonaid'] = row[2]
                session['zonaname'] = row[3]
                session['deptoid'] = row[4]
                session['deptoname'] = row[5]
                return redirect(url_for('captura_solicitud'))
        return redirect(url_for('home'))

    @app.route('/')
    @app.route('/home/')
    @app.route('/home/<token>')
    def home(token=None):
        urls = utils.get_res_url()
        return render_template('welcome.html', tok=token, urls=urls)

    @app.route('/about/')
    def about():
        urls = utils.get_res_url()
        return render_template('about.html', urls=urls)

    @app.route('/materiales/')
    def ver_material():
        if utils.is_logged_in(session):
            urls = utils.get_res_url()
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cols = ['id', 'Grupo', 'Precio Unitario', 'Unidad', 'Descripción']
            query = ("SELECT m.id_material, gm.nombre, m.precio_unitario, "
                     "m.unidad_medida, m.descripcion FROM materiales AS m "
                     " INNER JOIN grupo AS gm ON(gm.id_grupo=m.id_grupo);")
            cur = driver.connection.cursor()
            cur.execute(query)
            results = cur.fetchall()
            if len(results) == 0:
                results = None
            return render_template('catalogo.html', tipo='Materiales',
                                   urls=urls, columnas=cols, results=results)
        return redirect(url_for('home'))

    @app.route('/grupos/')
    def ver_grupo():
        if utils.is_logged_in(session):
            urls = utils.get_res_url()
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cols = ['id', 'Nombre']
            query = ("SELECT id_grupo, nombre FROM grupo;")
            cur = driver.connection.cursor()
            cur.execute(query)
            results = cur.fetchall()
            if len(results) == 0:
                results = None
            return render_template('catalogo.html', tipo='Grupos de Materiales',
                                   urls=urls, columnas=cols, results=results)
        return redirect(url_for('home'))

    @app.route('/usuarios/')
    def ver_usuario():
        if utils.is_logged_in(session):
            urls = utils.get_res_url()
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cols = ['id', 'Nombre', 'Departamento', 'Zona']
            query = ("SELECT u.id_usuario, u.nombre, d.nombre, z.nombre FROM usuarios AS u "
                     " INNER JOIN departamento AS d ON(d.id_departamento=u.id_departamento)"
                     " INNER JOIN zona AS z ON(z.id_zona=u.id_zona);")
            cur = driver.connection.cursor()
            cur.execute(query)
            results = cur.fetchall()
            if len(results) == 0:
                results = None
            return render_template('catalogo.html', tipo='Usuarios',
                                   urls=urls, columnas=cols, results=results)
        return redirect(url_for('home'))

    @app.route('/zonas/')
    def ver_zona():
        if utils.is_logged_in(session):
            urls = utils.get_res_url()
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cols = ['id', 'Nombre', 'Centro Gestor']
            query = ("SELECT z.id_zona, z.nombre, z.centrogestor FROM zona AS z;")
            cur = driver.connection.cursor()
            cur.execute(query)
            results = cur.fetchall()
            if len(results) == 0:
                results = None
            return render_template('catalogo.html', tipo='Zonas',
                                   urls=urls, columnas=cols, results=results)
        return redirect(url_for('home'))

    @app.route('/departamentos/')
    def ver_departamento():
        if utils.is_logged_in(session):
            urls = utils.get_res_url()
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cols = ['id', 'Nombre', 'Clave']
            query = (
                "SELECT d.id_departamento, d.nombre, d.c_clave FROM departamento AS d;")
            cur = driver.connection.cursor()
            cur.execute(query)
            results = cur.fetchall()
            if len(results) == 0:
                results = None
            return render_template('catalogo.html', tipo='Departamentos',
                                   urls=urls, columnas=cols, results=results)
        return redirect(url_for('home'))

    @app.route('/solicitudes/capturar/')
    def captura_solicitud():
        if utils.is_logged_in(session):
            urls = utils.get_res_url()
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cur = driver.connection.cursor()
            query = ("SELECT m.id_material, gm.nombre, m.precio_unitario, "
                     "m.unidad_medida, m.descripcion FROM materiales AS m "
                     " INNER JOIN grupo AS gm ON(gm.id_grupo=m.id_grupo);")
            cur.execute(query)
            mats = cur.fetchall()
            if len(mats) == 0:
                mats = None
            return render_template('captura.html', urls=urls, mats=mats)
        return redirect(url_for('home'))

    @app.route('/solicitudes/post/', methods=['POST'])
    def procesar_solicitud():
        if utils.is_logged_in(session):
            if request.method == 'POST':
                if (request.form.get('cantidad') is None or request.form.get('material') is None
                   or request.form.get('periodo') is None):
                    return '{"success":false}', {"Content-Type": "application/json"}
                if int(request.form['cantidad']) < 1:
                    return '{"success":false}', {"Content-Type": "application/json"}
                driver = database_driver.DatabaseDriver(
                    database_type=obj_ds["driver"], datasource_object=obj_ds)
                cur = driver.connection.cursor()
                query = "SELECT descripcion FROM periodo WHERE id_periodo = ? AND activo=1 "
                query += (" AND (fecha_inicio <= CURRENT_TIMESTAMP "
                          "AND fecha_fin >= CURRENT_TIMESTAMP)")
                params = []
                params.append(request.form['periodo'])
                cur.execute(query, params)
                arr = cur.fetchall()
                if len(arr) == 0:
                    return '{"success":false}', {"Content-Type": "application/json"}
                params.clear()
                params.append(request.form['material'])
                params.append(session['deptoid'])
                params.append(request.form['periodo'])
                params.append(session['zonaid'])
                query = ("SELECT m.id_material, p.id_periodo, m.descripcion, s.cantidad,"
                         " m.precio_unitario FROM solicitudes AS s "
                         " INNER JOIN departamento AS d ON(d.id_departamento=s.id_departamento)"
                         " INNER JOIN zona AS z ON(z.id_zona=s.id_zona)"
                         " INNER JOIN materiales AS m ON(m.id_material=s.id_material)"
                         " INNER JOIN periodo AS p ON(p.id_periodo = s.id_periodo)"
                         " WHERE s.id_material=? AND s.id_departamento=?"
                         " AND p.id_periodo=? AND s.id_zona=?")
                cur.execute(query, params)
                arr = cur.fetchall()
                params.clear()
                params.append(request.form['cantidad'])
                params.append(request.form['material'])
                params.append(session['zonaid'])
                params.append(session['deptoid'])
                params.append(request.form['periodo'])
                query = ("INSERT INTO solicitudes(cantidad,id_material,id_zona,"
                         "id_departamento,id_periodo) "
                         "VALUES(?, ?, ?, ?, ?);")
                if len(arr) > 0:
                    query = ("UPDATE solicitudes SET cantidad=? WHERE id_material=? "
                             "AND id_zona=? AND id_departamento=? AND id_periodo=?;")
                cur.execute(query, params)
                cur.connection.commit()
                return '{"success":true}', {"Content-Type": "application/json"}
            return '{"success":false}', {"Content-Type": "application/json"}
        return '{"success":false}', {"Content-Type": "application/json"}

    @app.route('/solicitudes/get/', methods=['POST'])
    def solicitudes_data():
        if utils.is_logged_in(session):
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cur = driver.connection.cursor()
            where = ""
            query = ("SELECT m.id_material, p.id_periodo, m.descripcion, s.cantidad,"
                     " m.unidad_medida, m.precio_unitario FROM solicitudes AS s "
                     " INNER JOIN departamento AS d ON(d.id_departamento=s.id_departamento)"
                     " INNER JOIN zona AS z ON(z.id_zona=s.id_zona)"
                     " INNER JOIN materiales AS m ON(m.id_material=s.id_material)"
                     " INNER JOIN periodo AS p ON(p.id_periodo = s.id_periodo)")
            where = " WHERE z.id_zona=? AND d.id_departamento=? AND p.id_periodo=? "
            params = []
            kjson = request.json
            params.append(kjson['id_zona'])
            params.append(kjson['id_departamento'])
            params.append(kjson['id_periodo'])
            if params:
                query += where
                cur.execute(query, params)
            else:
                cur.execute(query)
            k = cur.fetchall()
            if len(k) != 0:
                data = {}
                temp_params = []
                for row in k:
                    temp_row = []
                    cont = 0
                    for val in row:
                        if not isinstance(val, str):
                            if cont % 6 == 5:
                                temp_row.append(f'{val:0,.2f}')
                            else:
                                temp_row.append(str(val))
                        else:
                            temp_row.append(val)
                        cont += 1
                    temp_params.append(temp_row)
                data['headings'] = ['Id', 'Año', 'Material',
                                    'Cantidad', 'Unidad', 'Precio Unitario']
                data['data'] = temp_params
                return json.dumps(data), {"Content-Type": "application/json"}
            return '{"success":false}', {"Content-Type": "application/json"}
        return redirect(url_for('home'))

    @app.route('/solicitudes/delete/', methods=['POST'])
    def solicitudes_delete():
        if utils.is_logged_in(session):
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cur = driver.connection.cursor()
            query = ("DELETE FROM solicitudes WHERE id_zona=? "
                     "AND id_departamento=? AND id_material=?;")
            params = []
            kjson = request.json
            params.append(session['zonaid'])
            params.append(session['deptoid'])
            params.append(kjson['id_material'])
            cur.execute(query, params)
            cur.connection.commit()
            return '{"success":true}', {"Content-Type": "application/json"}
        return redirect(url_for('home'))

    @app.route('/periodo/')
    def periodo_ver():
        if utils.is_logged_in(session):
            urls = utils.get_res_url()
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cols = ['id', 'Nombre', 'Fecha Inicial', 'Fecha Final', 'Activo']
            query = (
                "SELECT id_periodo, descripcion, fecha_inicio, fecha_fin, activo FROM periodo;")
            cur = driver.connection.cursor()
            cur.execute(query)
            if cur.rowcount == 0:
                results = None
            else:
                results = cur.fetchall()
            return render_template('catalogo.html', tipo='Periodos de apertura',
                                   urls=urls, columnas=cols, results=results)
        return redirect(url_for('home'))

    @app.route('/periodo/get/', methods=['POST', 'GET'])
    def periodo_get():
        if utils.is_logged_in(session):
            driver = database_driver.DatabaseDriver(
                database_type=obj_ds["driver"], datasource_object=obj_ds)
            cur = driver.connection.cursor()
            query = ("SELECT id_periodo, descripcion, fecha_inicio, fecha_fin, activo FROM periodo "
                     " WHERE activo=1")
            kjson = request.json
            p_edit = kjson.get('editable')
            if p_edit is not None:
                query += (" AND (fecha_inicio > CURRENT_TIMESTAMP "
                          "OR fecha_fin < CURRENT_TIMESTAMP) ")
                if p_edit is True:
                    query += (" AND (fecha_inicio <= CURRENT_TIMESTAMP"
                              " AND fecha_fin >= CURRENT_TIMESTAMP) ")
            query += " ORDER BY fecha_inicio DESC;"
            cur.execute(query)
            k = cur.fetchall()
            if len(k) != 0:
                data = {}
                temp_params = []
                for row in k:
                    temp_row = []
                    cont = 0
                    for val in row:
                        if isinstance(val, datetime):
                            temp_row.append(val.isoformat())
                        else:
                            temp_row.append(val)
                        cont += 1
                    fecha_ini = temp_row[-3]
                    if isinstance(temp_row[-3], str):
                        fecha_ini = datetime.fromisoformat(temp_row[-3])
                    fecha_fin = temp_row[-2]
                    if isinstance(temp_row[-2], str):
                        fecha_fin = datetime.fromisoformat(temp_row[-2])
                    fecha_now = datetime.now()
                    lapse_ini = fecha_fin-fecha_now
                    lapse_final = fecha_ini-fecha_now
                    if lapse_final.total_seconds() < 0 and lapse_ini.total_seconds() > 0:
                        temp_row.append(True)
                    else:
                        temp_row.append(False)
                    temp_params.append(temp_row)
                data['headings'] = ['Id', 'Nombre',
                                    'Inicio', 'Fin', 'Activo', 'Editable']
                data['data'] = temp_params
                return json.dumps(data), {"Content-Type": "application/json"}
            return '{"success":false}', {"Content-Type": "application/json"}
        return redirect(url_for('home'))

    return app
