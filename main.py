"""
Proyecto Computacion I
======================
+ Grupo 1: Patricia Colmenares Carretero, Sofia Martinez Parada, Claudia Jazmin Soria Saavedra y Diego Vazquez Pares
+ Aplicacion para entrenamiento y testeo empleando validacion cruzada sobre archivos de texto con el fin de entrenar 
un modelo predictivo capaz de clasificar en funcion a dos categorias.
+ Se han utilizado los algoritmos de KNN, Naive-Bayes y Decision Tree.
"""

# librerias importadas
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QProgressBar, QMainWindow
from PyQt5.Qt import QTableWidgetItem, Qt
from PyQt5.uic import loadUi
from PyQt5.QtChart import QChart, QChartView, QValueAxis, QBarCategoryAxis, QBarSet, QBarSeries
from PyQt5.Qt import Qt
from funciones import *
from sklearn.metrics import recall_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from openpyxl import Workbook
import xlrd

# variables globales
noticias = []
despoblacion = []
desp = []
no_despoblacion = []

clases = []
processed_text_entrenamiento = []
processed_text_testeo = []

nuevas = []
cv = TfidfVectorizer()
vectorizer = CountVectorizer()

# inicializar UI
class initial(QDialog):
    def __init__(self):
        super(initial,self).__init__()
        loadUi("main.ui", self)
        # definir elementos de la UI y acciones/funciones asociadas

        # creamos sets para mostrar resultados en el barchart

        self.setRecall = QBarSet("Recalls")
        self.setRecall.append([0,0,0])
        self.setAccurracy = QBarSet("Accurracy")
        self.setAccurracy.append([0,0,0])

        self.series = QBarSeries()
        
        # Elementos Tab Entrenamiento:
        # ===========================

        # Btn Insertar primeros datos entrenamiento
        self.trainingAddFilesBtn.clicked.connect(self.insertarNoticiasEntrenamientoDespoblacion)

        # Btn Insertar segundos datos entrenamiento
        self.trainingAddFilesBtn2.clicked.connect(self.insertarNoticiasEntrenamientoNoDespoblacion)

        # Btn Preprocesamiento de texto
        self.procesarTextoBtn.clicked.connect(self.procesarTextoEntrenamiento)


        # ComboBox selector de Modelo a entrenar
        # self.chooseModelComboBox.activated.connect(self.elegirModeloEntrenamiento)

        # añadir elementos al comboBox y sus valores asociados
        self.chooseModelComboBox.addItem("KNN",1)
        self.chooseModelComboBox.addItem("Naive Bayes",2)
        self.chooseModelComboBox.addItem("Decision Tree",3)

        # Btn para entrenar el modelo seleccionado
        self.trainModelBtn.clicked.connect(self.entrenarModelo)

        # Elementos Tab Testeo:
        # ====================

        # Btn Insertar Datos Testeo
        self.testingFilesBtn.clicked.connect(self.insertarNoticiasTesteo)

        # Btn Seleccionar Modelo
        self.selectTestModelBtn.clicked.connect(self.elegirModeloTesteo)

        # Btn Mostrar Resultados
        self.testBtn.clicked.connect(self.mostrarResultados)

        # Elementos Tab
        # ===================
        self.nombreresultadoexcel = ':)'

    # funciones
    # =========
    # abrir dialog window para seleccionar los datos de entrenamiento
    def insertarNoticiasEntrenamientoDespoblacion(self):
        # abrir ventana seleccion archivos
        desp.append(self.openDialogBox())
        
        # cambiar texto campo descripcion
        self.stepTipsField.setPlainText("Seleccionamos los directorios donde tenemos los archivos de texto que utilizaremos para entrenar nuestro modelo.")
        
        #cambiar self.procesarTextoBtn a habilitado
        self.trainingAddFilesBtn2.setEnabled(True)

    # abrir dialog window para seleccionar los segundos datos de entrenamiento
    def insertarNoticiasEntrenamientoNoDespoblacion(self):
        # abrir ventana seleccion archivos
        no_despoblacion.append(self.openDialogBox())

        # cambiar texto campo descripcion
        self.stepTipsField.setPlainText("Seleccionamos los directorios donde tenemos los archivos de texto que utilizaremos para entrenar nuestro modelo.")

        #cambiar self.procesarTextoBtn a habilitado
        self.procesarTextoBtn.setEnabled(True)
    
    # aplicar preprocesamiento de texto
    def procesarTextoEntrenamiento(self):

        # cambiar texto campo descripcion
        self.stepTipsField.setPlainText("El preprocesamiento a realizar consta de 4 etapas:\n1. Tokenizar: separar las palabras que componen un texto, obteniendo como resultado una secuencia de tokens.\n2. Normalización: se pasa a minúsculas tdoos los tokens.\n3.Filtrado de stopwords: en esta etapa eliminamos  aquellas palabras con poco valor semántico, denominadas stopwords.\n4.Stemming: extraemos el lexema de los tokens restantes  (un ejemplo sería ‘cas-’ para la palabra ‘casero’)")

        # bucle inserción de noticias mediante open
        ingresar_noticias(desp[0], noticias)
        ingresar_noticias(no_despoblacion[0], noticias)
        ingresar_noticias(desp[0], despoblacion)

        # Procesamiento de texto
        texto_procesado(processed_text_entrenamiento, noticias)

        # Creación de arreglo de clases
        crea_clases(clases, processed_text_entrenamiento, despoblacion)

        # cambiar self.trainModelBtn a habilitado
        self.trainModelBtn.setEnabled(True)
        
        # cambiar texto campo descripcion
        self.stepTipsField.setPlainText("El preprocesamiento a realizar consta de 4 etapas:\n1. Tokenizar: separar las palabras que componen un texto, obteniendo como resultado una secuencia de tokens.\n2. Normalización: se pasa a minúsculas tdoos los tokens.\n3.Filtrado de stopwords: en esta etapa eliminamos  aquellas palabras con poco valor semántico, denominadas stopwords.\n4.Stemming: extraemos el lexema de los tokens restantes  (un ejemplo sería ‘cas-’ para la palabra ‘casero’).\n====================\nEl preprocesamiento ha acabado")
        
        # cambiar self.procesarTextoBtn a deshabilitado
        self.procesarTextoBtn.setEnabled(False)

    # abrir ventana seleccion archivos
    def openDialogBox(self):
        filenames = QFileDialog.getOpenFileNames()
        return filenames[0]

    # mostrar resultados testeo en nueva tabla
    def mostrarResultados(self):
        
        # para ocupar toda la tabla
        self.tableWidgetshowTest.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # resetear tabla
        self.tableWidgetshowTest.setRowCount(0)
        nombre = self.nombreresultadoexcel

        # mostrar contenido xlsx
        documento = xlrd.open_workbook(nombre+ '.xlsx')
        df = documento.sheet_by_index(0)
        self.tableWidgetshowTest.setRowCount(df.nrows)
        self.tableWidgetshowTest.setColumnCount(2)
        for x in range(1,df.nrows):
            for y in range(2):
                print ('x: ' +df.cell_value(x,y-1))
                item = QTableWidgetItem()
                nombreArchivo=df.cell_value(x,y-1).split("/")
                item.setText(nombreArchivo[len(nombreArchivo)-1])
                self.tableWidgetshowTest.setItem(x-1, y-1, item)

    # 
    def insertarNoticiasTesteo(self):
        # abrir ventana seleccion archivos
        filepaths = self.openDialogBox()

        #ingresar noticias
        ingresar_noticias(filepaths, nuevas)

        #Procesamiento de texto
        texto_procesado(processed_text_testeo, nuevas)
        # cambiar self.selectTestModelBtn a deshabilitado
        self.selectTestModelBtn.setEnabled(True)
        self.testingFilesBtn.setEnabled(False)

    #
    def elegirModeloTesteo(self):
        modelopath = self.openDialogBox()
        cv1 = cargar_modelo(modelopath[0])
        modelo = cargar_modelo(modelopath[1])

        X_testcv = tfid_fit(processed_text_testeo, cv1)

        predicciones = []


        for i in X_testcv:
            predicciones.append(prediccion(modelo, i))

        df = pd.DataFrame(data = predicciones, index = nuevas)
        print(df)
        archivo = modelopath[0]
        new_archivo = archivo.replace('modelos', 'resultados')
        nombre = new_archivo[:len(new_archivo)-3]
        self.nombreresultadoexcel = nombre
        df.to_excel(nombre + ".xlsx", "Sheet1")
        self.testBtn.setEnabled(True)

    #
    def entrenamientoNaiveBayes(self):
        # Proceso TFIDF
        X_traincv = cv.fit_transform(processed_text_entrenamiento)
        # Partición de datos
        X_train, X_test, Y_train, Y_test = train_test_split(X_traincv, clases, test_size=0.15, random_state=324)

        #Modelos
        naive = naive_bayes(X_train, Y_train)
        print(naive)
        print("####################### Test Score ##############################\n")
        test_score(naive, X_train, Y_train)

        # Creamos los datos a testear
        Y_true_naive, Y_pred_naive = datos_test(Y_test, naive, X_test)

        # Datos de los modelos
        print("###################### Accuracy ###############################\n")
        accuracy(Y_true_naive, Y_pred_naive)

        #incluir nueva accurracy al set de resultados de NaiveBayes
        #self.setNBayes.append(accuracy_score(Y_true_naive, Y_pred_naive) * 100)
        #self.setAccurracy[1]=accuracy_score(Y_true_naive, Y_pred_naive) * 100
        #self.a[1]=accuracy_score(Y_true_naive, Y_pred_naive) * 100
        
        self.setAccurracy.replace(1,accuracy_score(Y_true_naive, Y_pred_naive)*100)
        #llamar a funcion para actualizar los valores del Barchart
        
        print("####################### Recall ##############################\n")
        print(recall_score(Y_true_naive, Y_pred_naive, average='macro'))
        self.setRecall.replace(1,recall_score(Y_true_naive, Y_pred_naive, average='macro')*100)
        a= "Modelo Naive-Bayes\n==================\nRecall:" + str(recall_score(Y_true_naive, Y_pred_naive, average='macro')) + "\nPrecision: " + str(accuracy_score(Y_true_naive, Y_pred_naive))
        self.stepTipsField.setPlainText(a)
        self.appendResults()
        print("\n###################### Matriz de confusion ###############################\n")
        matrizconf(Y_true_naive, Y_pred_naive)

        #Guardamos modelo
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("dia_%d-%m-%Y,hora_%H-%M-%S")
        guardar_modelo('modelos/naive_' + dt_string, naive)

        with open('modelos/naive_' + dt_string + '.pk', 'wb') as f:
            pickle.dump(cv, f)

    #
    def entrenamientoArbolDecision(self):
        # Proceso TFIDF
        X_traincv = cv.fit_transform(processed_text_entrenamiento)
        #Partición de datos
        X_train, X_test, Y_train, Y_test = train_test_split(X_traincv, clases, test_size=0.15, random_state=324)

        #Modelos
        tree = decision_tree(X_train, Y_train)
        print("####################### Test Score ##############################\n")
        test_score(tree, X_train, Y_train)

        #Creamos los datos a testear
        Y_true_tree, Y_pred_tree = datos_test(Y_test, tree, X_test)


        #Datos de los modelos
        print("###################### Accuracy ###############################\n")
        accuracy(Y_true_tree, Y_pred_tree)

        #incluir nueva accurracy al set de resultados de NaiveBayes
        #self.setDTrees.append(accuracy_score(Y_true_tree, Y_pred_tree)*100)
        self.setAccurracy.replace(2,accuracy_score(Y_true_tree, Y_pred_tree)*100)
        #llamar a funcion para actualizar los valores del Barchart
        
        print("####################### Recall ##############################\n")
        print(recall_score(Y_true_tree,Y_pred_tree, average='macro'))
        #self.setDTrees.append(recall_score(Y_true_tree, Y_pred_tree, average='macro')*100)
        self.setRecall.replace(2,recall_score(Y_true_tree, Y_pred_tree, average='macro')*100)
        a= "Modelo Arbol Decision\n=====================\nRecall:" + str(recall_score(Y_true_tree, Y_pred_tree, average='macro')) + "\nPrecision: " + str(accuracy_score(Y_true_tree, Y_pred_tree))
        self.stepTipsField.setPlainText(a)
        self.appendResults()
        #Matriz confusion
        print("\n###################### Matriz de confusion ###############################\n")
        matrizconf(Y_true_tree, Y_pred_tree)


        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("dia_%d-%m-%Y,hora_%H-%M-%S")
        print("date and time =", dt_string)    
        guardar_modelo('modelos/tree_' + dt_string, tree)

        with open('modelos/tree_' + dt_string + '.pk', 'wb') as f:
            pickle.dump(cv, f)

    #
    def entrenamientoKnn(self):
        # Proceso TFIDF
        X_traincv = cv.fit_transform(processed_text_entrenamiento)
        #Partición de datos
        X_train, X_test, Y_train, Y_test = train_test_split(X_traincv, clases, test_size=0.15, random_state=324)

        #Modelos
        modknn = knn(X_train, Y_train)

        print("####################### Test Score ##############################\n")
        test_score(modknn, X_train, Y_train)

        #Creamos los datos a testear
        Y_true_knn, Y_pred_knn = datos_test(Y_test, modknn, X_test)


        #Datos de los modelos
        print("###################### Accuracy ###############################\n")

        accuracy(Y_true_knn, Y_pred_knn)

        #llamar a funcion para actualizar los valores del Barchart
        self.setAccurracy.replace(0,accuracy_score(Y_true_knn, Y_pred_knn)*100)

        print("####################### Recall ##############################\n")
        print(recall_score(Y_true_knn, Y_pred_knn, average='macro'))
        
        #self.setDTrees.append(recall_score(Y_true_knn, Y_pred_knn, average='macro')*100)
        self.setRecall.replace(0,recall_score(Y_true_knn, Y_pred_knn, average='macro')*100)
        a= "Modelo KNN\n===============\nRecall:" + str(recall_score(Y_true_knn, Y_pred_knn, average='macro')) + "\nPrecision: " + str(accuracy_score(Y_true_knn, Y_pred_knn))
        self.stepTipsField.setPlainText(a)
        self.appendResults()
        #Matriz confusion
        print("\n###################### Matriz de confusion ###############################\n")
        matrizconf(Y_true_knn, Y_pred_knn)

        #Guardamos modelo
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("dia_%d-%m-%Y,hora_%H-%M-%S")
        print("date and time =", dt_string)    
        guardar_modelo('modelos/knn_' + dt_string, modknn)

        with open('modelos/knn_' + dt_string + '.pk', 'wb') as f:
            pickle.dump(cv, f)

    #
    def entrenarModelo(self):
        #cambiar texto en self.stepTipsField
        self.stepTipsField.setPlainText(" Entrenando el modelo seleccionado")
        
        #tomar valor actual del comboBox
        modelSelect = self.chooseModelComboBox.currentData()
        print( "opcion seleccionada:",modelSelect)
        #no existe switch en python (o.o)
        if modelSelect == 1:
            self.entrenamientoKnn()

        if modelSelect == 2:
            self.entrenamientoNaiveBayes()

        if modelSelect == 3:
            self.entrenamientoArbolDecision()

    # add resultados entrenamiento y actualizar barchart
    def appendResults(self):
        #clear de series
        self.series = QBarSeries()

        #add series de todos los modelos procesados
        self.series.append(self.setAccurracy)
        self.series.append(self.setRecall)

        chart = QChart()
        
        chart.addSeries(self.series)
        chart.setTitle("Precisiones de Modelos")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        modelosEjeX = ('KNN', 'Naive Bayes', 'Decision Trees')

        ejeX = QBarCategoryAxis()
        ejeX.append(modelosEjeX)

        ejeY = QValueAxis()

        chart.addAxis(ejeX,Qt.AlignBottom)
        chart.addAxis(ejeY,Qt.AlignLeft)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        self.QChartView = QChartView(chart)
        self.QChartView.resize(600,600)
        self.QChartView.show()


#inicializar app
app=QtWidgets.QApplication(sys.argv)
#crear instancia clase initial
mainwindow=initial()


#Stack
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.show()
app.exec()
