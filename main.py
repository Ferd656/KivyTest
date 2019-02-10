# -*- coding: utf-8 -*-
# Python 2.7
import os
import sqlite3

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.config import Config

Config.set("graphics", "width", "340")
Config.set("graphics", "height", "640")


def connect_to_database(path):
    try:
        conn = sqlite3.connect(path)
        crear_tabla(conn)
        conn.close()
    except Exception as e:
        print(e)


def crear_tabla(conn):
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS soluciones "
                "(nombre TEXT UNIQUE, "
                "moneda INTEGER, "
                "tasa REAL,"
                "plazo INTEGER)")
    conn.commit()


class MensajePopUp(Popup):
    pass


class LienzoApp(ScreenManager):
    def __init__(self):
        super(LienzoApp,self).__init__()
        self.APP_PATH = os.getcwd()
        self.DB_PATH = self.APP_PATH+"/testdb.db"
        self.InicioLienzo = InicioLienzo(self)
        self.DBWid = DBWid(self)
        self.InsertarDataWid = BoxLayout()
        self.ActualizaCajas = BoxLayout()
        self.popup = MensajePopUp()

        wid = Screen(name="inicio")
        wid.add_widget(self.InicioLienzo)
        self.add_widget(wid)

        wid = Screen(name="productos")
        wid.add_widget(self.DBWid)
        self.add_widget(wid)

        wid = Screen(name="insertardatos")
        wid.add_widget(self.InsertarDataWid)
        self.add_widget(wid)

        wid = Screen(name="actualizar")
        wid.add_widget(self.ActualizaCajas)
        self.add_widget(wid)

        self.goto_inicio()

    def goto_inicio(self):
        self.current = "inicio"

    def goto_soluciones(self):
        self.DBWid.check_memory()
        self.current = "productos"

    def goto_insertar(self):
        self.InsertarDataWid.clear_widgets()
        wid = InsertarDataWid(self)
        self.InsertarDataWid.add_widget(wid)
        self.current = "insertardatos"

    def goto_actualizar(self, data_id):
        self.ActualizaCajas.clear_widgets()
        wid = ActualizaCajas(self, data_id)
        self.ActualizaCajas.add_widget(wid)
        self.current = "actualizar"

class InicioLienzo(BoxLayout):
    def __init__(self, LienzoAppInfo):
        super(InicioLienzo,self).__init__()
        self.LienzoAppInfo = LienzoAppInfo

    def crear_db(self):
        connect_to_database(self.LienzoAppInfo.DB_PATH)
        self.LienzoAppInfo.goto_soluciones()

    def Salir_de_App(self):
        App.get_running_app().stop()


class DBWid(BoxLayout):
    def __init__(self, LienzoApp):
        super(DBWid,self).__init__()
        self.mainwid = LienzoApp

    def check_memory(self):
        self.ids.container.clear_widgets()
        wid = NewDataButton(self.mainwid)
        self.ids.container.add_widget(wid)

        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cur = conn.cursor()
        sql_str = "SELECT * FROM soluciones"
        cur.execute(sql_str)

        for i in cur:
            wid = CajasDatos(self.mainwid)
            r1 = "Nombre: " + i[0] + "\n"
            r2 = "Moneda: " + str(i[1]) + "\n"
            r3 = "Tasa: " + str(i[2]) + "\n"
            r4 = "Plazo: " + str(i[3])
            wid.data_id = i[0]
            wid.data = r1 + r2 + r3 + r4
            self.ids.container.add_widget(wid)

        conn.close()

class InsertarDataWid(BoxLayout):
    def __init__(self, LienzoApp):
        super(InsertarDataWid,self).__init__()
        self.mainwid = LienzoApp

    def insertar_data(self):
        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cur = conn.cursor()
        d1 = self.ids.ti_Nombre.text
        d2 = self.ids.ti_Moneda.text
        d3 = self.ids.ti_Tasa.text
        d4 = self.ids.ti_Plazo.text
        try:
            mi_tupla = (d1, int(d2), float(d3), float(d4))
            sql_str = "INSERT INTO soluciones " \
                      "(nombre, moneda, tasa, plazo) " \
                      "VALUES(?,?,?,?)"
            cur.execute(sql_str, mi_tupla)
            conn.commit()
            conn.close()
            self.mainwid.goto_soluciones()
        except Exception as e:
            mnsj = self.mainwid.popup.ids.mensaje
            self.mainwid.popup.open()
            self.mainwid.popup.title = "Ha ocurrido un error"
            mnsj.text = str(e)

    def volver(self):
        self.mainwid.goto_soluciones()


class ActualizaCajas(BoxLayout):
    def __init__(self, LienzoApp, data_id):
        super(ActualizaCajas,self).__init__()
        self.mainwid = LienzoApp
        self.data_id = data_id
        self.consultar()

    def consultar(self):
        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cur = conn.cursor()
        sql_str = "SELECT * FROM soluciones " \
                  "WHERE nombre = ?"
        cur.execute(sql_str, [self.data_id])
        mi_lista = cur.fetchall()
        self.ids.ti_Moneda.text = str(mi_lista[0][1])
        self.ids.ti_Tasa.text = str(mi_lista[0][2])
        self.ids.ti_Plazo.text = str(mi_lista[0][3])
        conn.close()

    def actualizar_data(self):
        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cur = conn.cursor()
        d1 = self.data_id
        d2 = self.ids.ti_Moneda.text
        d3 = self.ids.ti_Tasa.text
        d4 = self.ids.ti_Plazo.text
        try:
            mi_tupla = (d1, int(d2), float(d3), float(d4), d1)
            sql_str = "UPDATE soluciones SET " \
                      "nombre = ?, moneda = ?, tasa = ?, " \
                      "plazo = ? WHERE nombre = ?"
            cur.execute(sql_str, mi_tupla)
            conn.commit()
            conn.close()
            self.mainwid.goto_soluciones()
        except Exception as e:
            mnsj = self.mainwid.popup.ids.mensaje
            self.mainwid.popup.open()
            self.mainwid.popup.title = "Ha ocurrido un error"
            mnsj.text = str(e)

    def eliminar(self):
        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cur = conn.cursor()
        try:
            sql_str = "DELETE FROM soluciones " \
                      "WHERE nombre = ?"
            cur.execute(sql_str, [self.data_id])
            conn.commit()
            conn.close()
            self.mainwid.goto_soluciones()
        except Exception as e:
            mnsj = self.mainwid.popup.ids.mensaje
            self.mainwid.popup.open()
            self.mainwid.popup.title = "Ha ocurrido un error"
            mnsj.text = str(e)

    def salir(self):
        self.mainwid.goto_soluciones()


class CajasDatos(BoxLayout):
    def __init__(self, LienzoApp):
        super(CajasDatos,self).__init__()
        self.mainwid = LienzoApp

    def actualizar(self, data_id):
        self.mainwid.goto_actualizar(data_id)

class NewDataButton(BoxLayout):
    def __init__(self, LienzoApp):
        super(NewDataButton,self).__init__()
        self.mainwid = LienzoApp

    def crear_solucion(self):
        self.mainwid.goto_insertar()

    def volver_a_inicio(self):
        self.mainwid.goto_inicio()


class MainApp(App):
    title = "Prueba SQLite"

    def build(self):
        return LienzoApp()


if __name__ == '__main__':
    MainApp().run()
