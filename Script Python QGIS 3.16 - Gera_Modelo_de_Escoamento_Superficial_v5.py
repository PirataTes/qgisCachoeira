"""
Model exported as python.
Name : Alg Rede e Sub Bacias
Group : Rede e Sub Bacias
With QGIS : 31602
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterExpression
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsExpression
import processing
import csv
import os


class AlgRedeESubBacias(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('AmostrasdeTreino', 'Amostras de Treino (com campo id)', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('AreadeInteresse', 'Area de Interesse', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('ImagemdeSatlite', 'Imagem de Satélite', defaultValue=None))
        self.addParameter(QgsProcessingParameterExpression('TrechoparaserExcluido', 'Trecho para ser Excluido', optional=True, parentLayerParameterName='', defaultValue=''))
        self.addParameter(QgsProcessingParameterVectorLayer('camadaLinhatabelaVazia', 'Camada de Ruas', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('rasterDEM', 'rasterDEM', defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Log detalhado', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink('Trechoscsv', 'TrechosCSV', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=False, defaultValue='C:/Users/leona/OneDrive/Área de Trabalho/IC_UFSJ/ANEW_PROJ/TrechoCSV-mod.csv'))
        self.addParameter(QgsProcessingParameterFeatureSink('PontosCsv', 'Pontos CSV', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='C:/Users/leona/OneDrive/Área de Trabalho/IC_UFSJ/ANEW_PROJ/PontosCSV_L-mod.csv'))
        self.addParameter(QgsProcessingParameterFeatureSink('Desenho', 'desenho', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='C:/Users/leona/OneDrive/Área de Trabalho/IC_UFSJ/ANEW_PROJ/desenho_subBacia.csv'))
        self.addParameter(QgsProcessingParameterFeatureSink('PontosShp', 'Pontos SHP', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Trechosshp', 'TrechosSHP', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('TabelaAreas', 'Tabela Areas', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='C:/Users/leona/OneDrive/Área de Trabalho/IC_UFSJ/ANEW_PROJ/Tabela Areas.csv'))
        self.addParameter(QgsProcessingParameterFeatureSink('PontosEscoamento', 'Pontos Escoamento', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='C:/Users/leona/OneDrive/Área de Trabalho/IC_UFSJ/ANEW_PROJ/Pontos Escoamento.csv'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(59, model_feedback)
        results = {}
        outputs = {}

        # Definir projeção raster DEM_area
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:32723'),
            'INPUT': parameters['ImagemdeSatlite']
        }
        outputs['DefinirProjeoRasterDem_area'] = processing.run('gdal:assignprojection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Ruas Reprojetada
        alg_params = {
            'INPUT': parameters['camadaLinhatabelaVazia'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:32723'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RuasReprojetada'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Remover Waterways
        alg_params = {
            'FIELD': 'waterway',
            'INPUT': outputs['RuasReprojetada']['OUTPUT'],
            'OPERATOR': 1,
            'VALUE': '\'NULL\'',
            'FAIL_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RemoverWaterways'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Definir projeção area de interesse
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:32723'),
            'INPUT': parameters['AreadeInteresse'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DefinirProjeoAreaDeInteresse'] = processing.run('native:assignprojection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Regiao Reprojetada
        alg_params = {
            'INPUT': parameters['AreadeInteresse'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:32723'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RegiaoReprojetada'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Train algorithm
        alg_params = {
            'INPUT_COLUMN': 'id',
            'INPUT_LAYER': parameters['AmostrasdeTreino'],
            'INPUT_RASTER': outputs['DefinirProjeoRasterDem_area']['OUTPUT'],
            'PARAMGRID': '',
            'SPLIT_PERCENT': 50,
            'TRAIN': 0,
            'OUTPUT_MATRIX': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_MODEL': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TrainAlgorithm'] = processing.run('dzetsaka:Train algorithm', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Recortar satelite com area 
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,
            'EXTRA': '',
            'INPUT': outputs['DefinirProjeoRasterDem_area']['OUTPUT'],
            'KEEP_RESOLUTION': False,
            'MASK': outputs['DefinirProjeoAreaDeInteresse']['OUTPUT'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': None,
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:32723'),
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RecortarSateliteComArea'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Amortecedor - aumentar a area de interesse
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 20,
            'END_CAP_STYLE': 0,
            'INPUT': outputs['RegiaoReprojetada']['OUTPUT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AmortecedorAumentarAAreaDeInteresse'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Amortecedor
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 5,
            'END_CAP_STYLE': 0,
            'INPUT': outputs['RuasReprojetada']['OUTPUT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Amortecedor'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Diferença
        alg_params = {
            'INPUT': outputs['RegiaoReprojetada']['OUTPUT'],
            'OVERLAY': outputs['Amortecedor']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Diferena'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Apagar tabela
        alg_params = {
            'COLUMN': QgsExpression('\'osm_id;name;highway;waterway;aerialway;barrier;man_made;z_order;other_tags\'').evaluate(),
            'INPUT': outputs['RemoverWaterways']['FAIL_OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ApagarTabela'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Classificacao
        alg_params = {
            'INPUT_MASK': None,
            'INPUT_MODEL': outputs['TrainAlgorithm']['OUTPUT_MODEL'],
            'INPUT_RASTER': outputs['RecortarSateliteComArea']['OUTPUT'],
            'OUTPUT_RASTER': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Classificacao'] = processing.run('dzetsaka:Predict model (classification map)', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Recortar raster pela camada de máscara
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,
            'EXTRA': '',
            'INPUT': parameters['rasterDEM'],
            'KEEP_RESOLUTION': False,
            'MASK': outputs['AmortecedorAumentarAAreaDeInteresse']['OUTPUT'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': None,
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:32723'),
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RecortarRasterPelaCamadaDeMscara'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Polígonos para linhas
        alg_params = {
            'INPUT': outputs['Diferena']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolgonosParaLinhas'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Recortar
        alg_params = {
            'INPUT': outputs['ApagarTabela']['OUTPUT'],
            'OVERLAY': outputs['RegiaoReprojetada']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Recortar'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Raster para vetor (poligonizar)
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['Classificacao']['OUTPUT_RASTER'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterParaVetorPoligonizar'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Corrigir geometrias vetorizado
        alg_params = {
            'INPUT': outputs['RasterParaVetorPoligonizar']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CorrigirGeometriasVetorizado'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Reprojetar camada
        alg_params = {
            'INPUT': outputs['Recortar']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:32723'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojetarCamada'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Definir projeção raster DEM
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:32723'),
            'INPUT': outputs['RecortarRasterPelaCamadaDeMscara']['OUTPUT']
        }
        outputs['DefinirProjeoRasterDem'] = processing.run('gdal:assignprojection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Extrair vértices
        alg_params = {
            'INPUT': outputs['ReprojetarCamada']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairVrtices'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Excluir geometrias duplicadas
        alg_params = {
            'INPUT': outputs['ExtrairVrtices']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExcluirGeometriasDuplicadas'] = processing.run('native:deleteduplicategeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Poligonize
        alg_params = {
            'INPUT': outputs['PolgonosParaLinhas']['OUTPUT'],
            'KEEP_FIELDS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Poligonize'] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Descartar campo(s)
        alg_params = {
            'COLUMN': QgsExpression('\'vertex_index;vertex_part;vertex_part_index;distance;angle\'').evaluate(),
            'INPUT': outputs['ExcluirGeometriasDuplicadas']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DescartarCampos'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Explodir linhas
        alg_params = {
            'INPUT': outputs['ReprojetarCamada']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExplodirLinhas'] = processing.run('native:explodelines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Reprojetar camada subBacias
        alg_params = {
            'INPUT': outputs['Poligonize']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:32723'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojetarCamadaSubbacias'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Pixels de raster para pontos
        alg_params = {
            'FIELD_NAME': 'VALUE',
            'INPUT_RASTER': outputs['DefinirProjeoRasterDem']['OUTPUT'],
            'RASTER_BAND': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PixelsDeRasterParaPontos'] = processing.run('native:pixelstopoints', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # adicionar id Pontos
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'id',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': '$id',
            'INPUT': outputs['DescartarCampos']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdicionarIdPontos'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # adicionar id Sub bacias subbacia separada
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'id_subBacia',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': '$id',
            'INPUT': outputs['ReprojetarCamadaSubbacias']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdicionarIdSubBaciasSubbaciaSeparada'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # adicionar id Trechos
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'id',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': '$id',
            'INPUT': outputs['ExplodirLinhas']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdicionarIdTrechos'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Extrair vértices subBacias
        alg_params = {
            'INPUT': outputs['AdicionarIdSubBaciasSubbaciaSeparada']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairVrticesSubbacias'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Recortar classificado com subbacias
        alg_params = {
            'INPUT': outputs['CorrigirGeometriasVetorizado']['OUTPUT'],
            'OVERLAY': outputs['AdicionarIdSubBaciasSubbaciaSeparada']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RecortarClassificadoComSubbacias'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # ELEVATION Calculadora de campo
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'ELEVATION',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': '\"VALUE\"',
            'INPUT': outputs['PixelsDeRasterParaPontos']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ElevationCalculadoraDeCampo'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Excluir geometrias duplicadas subBacias
        alg_params = {
            'INPUT': outputs['ExtrairVrticesSubbacias']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExcluirGeometriasDuplicadasSubbacias'] = processing.run('native:deleteduplicategeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Extrair por atributo apenas tipo 1
        alg_params = {
            'FIELD': QgsExpression('\'DN\'').evaluate(),
            'INPUT': outputs['RecortarClassificadoComSubbacias']['OUTPUT'],
            'OPERATOR': 0,
            'VALUE': '1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairPorAtributoApenasTipo1'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Colocar area nas sub bacias
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'area',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': '$area',
            'INPUT': outputs['AdicionarIdSubBaciasSubbaciaSeparada']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ColocarAreaNasSubBacias'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Recortar sub bacias apenas areas tipo 1
        alg_params = {
            'INPUT': outputs['AdicionarIdSubBaciasSubbaciaSeparada']['OUTPUT'],
            'OVERLAY': outputs['ExtrairPorAtributoApenasTipo1']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RecortarSubBaciasApenasAreasTipo1'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Descartar campo(s) subBacias
        alg_params = {
            'COLUMN': QgsExpression('\'vertex_part;vertex_part_index;vertex_part_ring;distance;angle\'').evaluate(),
            'INPUT': outputs['ExcluirGeometriasDuplicadasSubbacias']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DescartarCamposSubbacias'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # adicionar x_ini
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'x_ini',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,
            'FORMULA': '$x_at(0)',
            'INPUT': outputs['AdicionarIdTrechos']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdicionarX_ini'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Colocar area nas regioes tipo 1
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': QgsExpression('\'area1\'').evaluate(),
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': '$area',
            'INPUT': outputs['RecortarSubBaciasApenasAreasTipo1']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ColocarAreaNasRegioesTipo1'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Descartar campo(s) DEM
        alg_params = {
            'COLUMN': QgsExpression('\'VALUE\'').evaluate(),
            'INPUT': outputs['ElevationCalculadoraDeCampo']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DescartarCamposDem'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # adicionar y_ini
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'y_ini',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,
            'FORMULA': '$y_at(0)',
            'INPUT': outputs['AdicionarX_ini']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdicionarY_ini'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # adicionar x_fin
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'x_fin',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,
            'FORMULA': '$x_at(-1)',
            'INPUT': outputs['AdicionarY_ini']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdicionarX_fin'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Unir atributos pelo mais próximo
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': QgsExpression('\'ELEVATION\'').evaluate(),
            'INPUT': outputs['AdicionarIdPontos']['OUTPUT'],
            'INPUT_2': outputs['DescartarCamposDem']['OUTPUT'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['UnirAtributosPeloMaisPrximo'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Associar atributos por local
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['ColocarAreaNasSubBacias']['OUTPUT'],
            'JOIN': outputs['ColocarAreaNasRegioesTipo1']['OUTPUT'],
            'JOIN_FIELDS': QgsExpression('\'area1\'').evaluate(),
            'METHOD': 0,
            'PREDICATE': [0,3,4,5],
            'PREFIX': '',
            'OUTPUT': parameters['TabelaAreas']
        }
        outputs['AssociarAtributosPorLocal'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['TabelaAreas'] = outputs['AssociarAtributosPorLocal']['OUTPUT']

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # adicionar X desenho
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'X',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,
            'FORMULA': '$x',
            'INPUT': outputs['DescartarCamposSubbacias']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdicionarXDesenho'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Unir atributos pelo mais próximo subBacias
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': QgsExpression('\'ELEVATION\'').evaluate(),
            'INPUT': outputs['DescartarCamposSubbacias']['OUTPUT'],
            'INPUT_2': outputs['DescartarCamposDem']['OUTPUT'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['UnirAtributosPeloMaisPrximoSubbacias'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Descartar campo(s)
        alg_params = {
            'COLUMN': QgsExpression('\'n;distance;feature_x;feature_y;nearest_x;nearest_y\'').evaluate(),
            'INPUT': outputs['UnirAtributosPeloMaisPrximo']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DescartarCampos'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # adicionar y_fin
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'y_fin',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,
            'FORMULA': '$y_at(-1)',
            'INPUT': outputs['AdicionarX_fin']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdicionarY_fin'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # adicionar Y desenho
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Y',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,
            'FORMULA': '$y',
            'INPUT': outputs['AdicionarXDesenho']['OUTPUT'],
            'OUTPUT': parameters['Desenho']
        }
        outputs['AdicionarYDesenho'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Desenho'] = outputs['AdicionarYDesenho']['OUTPUT']

        feedback.setCurrentStep(49)
        if feedback.isCanceled():
            return {}

        # Adicionar comprimento
        alg_params = {
            'FIELD_LENGTH': 4,
            'FIELD_NAME': 'Comprimento',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': 'if($length>1,$length,1)\r\n\t',
            'INPUT': outputs['AdicionarY_fin']['OUTPUT'],
            'OUTPUT': parameters['Trechosshp']
        }
        outputs['AdicionarComprimento'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Trechosshp'] = outputs['AdicionarComprimento']['OUTPUT']

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # adicionar x
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'x',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,
            'FORMULA': '$x',
            'INPUT': outputs['DescartarCampos']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdicionarX'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Descartar campo(s) valt desenho
        alg_params = {
            'COLUMN': QgsExpression('\'vertex_index;n;distance;feature_x;feature_y;nearest_x;nearest_y\'').evaluate(),
            'INPUT': outputs['UnirAtributosPeloMaisPrximoSubbacias']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DescartarCamposValtDesenho'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # adicionar y CSV
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'y',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,
            'FORMULA': '$y',
            'INPUT': outputs['AdicionarX']['OUTPUT'],
            'OUTPUT': parameters['PontosCsv']
        }
        outputs['AdicionarYCsv'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PontosCsv'] = outputs['AdicionarYCsv']['OUTPUT']

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Adicionar comprimento csv
        alg_params = {
            'FIELD_LENGTH': 4,
            'FIELD_NAME': 'Comprimento',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': 'if($length>1,$length,1)\r\n\t',
            'INPUT': outputs['AdicionarY_fin']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdicionarComprimentoCsv'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # adicionar y
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'y',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,
            'FORMULA': '$y',
            'INPUT': outputs['AdicionarX']['OUTPUT'],
            'OUTPUT': parameters['PontosShp']
        }
        outputs['AdicionarY'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PontosShp'] = outputs['AdicionarY']['OUTPUT']

        feedback.setCurrentStep(55)
        if feedback.isCanceled():
            return {}

        # Extrair por expressão pontos baixos subBacias
        alg_params = {
            'EXPRESSION': QgsExpression('\'elevation = minimum(  \"ELEVATION\" ,  \"id_subBacia\"  ,  \"id_subBacia\"  )\'').evaluate(),
            'INPUT': outputs['DescartarCamposValtDesenho']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairPorExpressoPontosBaixosSubbacias'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(56)
        if feedback.isCanceled():
            return {}

        # Unir atributos pelo mais próximo Guia
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['x','y'],
            'INPUT': outputs['ExtrairPorExpressoPontosBaixosSubbacias']['OUTPUT'],
            'INPUT_2': outputs['AdicionarY']['OUTPUT'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['UnirAtributosPeloMaisPrximoGuia'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(57)
        if feedback.isCanceled():
            return {}

        # Extrair por atributo trecho ciclico
        alg_params = {
            'FIELD': 'id',
            'INPUT': outputs['AdicionarComprimentoCsv']['OUTPUT'],
            'OPERATOR': 0,
            'VALUE': parameters['TrechoparaserExcluido'],
            'FAIL_OUTPUT': parameters['Trechoscsv'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairPorAtributoTrechoCiclico'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Trechoscsv'] = outputs['ExtrairPorAtributoTrechoCiclico']['FAIL_OUTPUT']

        feedback.setCurrentStep(58)
        if feedback.isCanceled():
            return {}

        # Descartar campo(s) Pontos Escoamento
        alg_params = {
            'COLUMN': QgsExpression('\'ELEVATION;n;distance;feature_x;feature_y;nearest_x;nearest_y\'').evaluate(),
            'INPUT': outputs['UnirAtributosPeloMaisPrximoGuia']['OUTPUT'],
            'OUTPUT': parameters['PontosEscoamento']
        }
        outputs['DescartarCamposPontosEscoamento'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PontosEscoamento'] = outputs['DescartarCamposPontosEscoamento']['OUTPUT']
        
    # MANIPULANDO OS ARQUIVOS TXT PARA IMPORTAR OS DADOS DOS PONTOS E DAS LINHAS

        pontosCSV = results['PontosCsv']
        trechosCSV = results['Trechoscsv']
        pontosDesenho = results['Desenho']
        pontosRedeEscoamento = results['PontosEscoamento']
        tabelaAreas = results['TabelaAreas']
        

        def function_ret_carac(obj_ler_arquivo):
           lista_nova=[] 
           for linha in obj_ler_arquivo:
               line_rem_carac = linha.rstrip()
               line_rem_subs = line_rem_carac.replace('"', '')
               line_divid = line_rem_subs.split(',')
               lista_nova.append(line_divid)
           del lista_nova[0]
           return lista_nova

###1 parte####   
#Recebe arquivo csv para leitura
        tabelaAreas=r"C:\Users\leona\OneDrive\Área de Trabalho\IC_UFSJ\ANEW_PROJ\Tabela Areas.csv" 
        arquivo_Area = open(tabelaAreas, 'r')
        lista_tab_Area = []
        lista_tab_Area=function_ret_carac(arquivo_Area)
#Remove coluna duplica no csv
        for i in range(0,len(lista_tab_Area)):
            del lista_tab_Area[i][1]
#Recebe a primeira coluna na lista 'lista_num_bacia' 
        lista_num_bacia=[]
        for i in range(0,len(lista_tab_Area)):
            lista_num_bacia.append(lista_tab_Area[i][0])
#Recebe a segunda coluna na lista 'lista_num_bacia'
        lista_area=[]
        for i in range(0,len(lista_tab_Area)):
            lista_area.append(lista_tab_Area[i][1])

###2 parte####
#Recebe arquivo csv para leitura
        tabelaEscoa=r"C:\Users\leona\OneDrive\Área de Trabalho\IC_UFSJ\ANEW_PROJ\Pontos Escoamento.csv" 
        arquivo_Escoa = open(tabelaEscoa, 'r')
        lista_tab_Escoa = []
        lista_tab_Escoa=function_ret_carac(arquivo_Escoa)

###3 parte####
#Recebe arquivo csv para leitura
        tabelaNOS=r"C:\Users\leona\OneDrive\Área de Trabalho\IC_UFSJ\ANEW_PROJ\PontosCSV_L-mod.csv" 
        arquivo_Nos = open(tabelaNOS, 'r')
        lista_tab_Nos = []
        lista_tab_Nos=function_ret_carac(arquivo_Nos)
#Remove coluna 0 e 1
        for i in range(0,len(lista_tab_Nos)):
            del lista_tab_Nos[i][0] 
            del lista_tab_Nos[i][1]
#Compara tabelas e recebe linha caso string da posição seja igual
        lista_total=[]
        for i in range(0,len(lista_tab_Escoa)):
            for j in range(0,len(lista_tab_Nos)):
                if lista_tab_Escoa[i][1]==lista_tab_Nos[j][1] and lista_tab_Escoa[i][2]==lista_tab_Nos[j][2]:
                    string_tabs=lista_tab_Escoa[i]+lista_tab_Nos[j]
                    lista_total.append(string_tabs)

        for i in range(1,len(lista_total)):
            for j in range(0,len(lista_total)):
                if lista_total[i][0]==lista_total[j][0]:
                    lista_total[j]=lista_total[i]

        lista_total[:] = [x for i, x in enumerate(lista_total) if i == lista_total.index(x)]
#Recebe a coluna 0 na lista
        lista_bacias=[]
        for i in range(0,len(lista_total)):
            lista_bacias.append(lista_total[i][0])

#Recebe a coluna 3 na lista
        lista_no_sep=[]
        for i in range(0,len(lista_total)):
           lista_no_sep.append(lista_total[i][3])

        lista_nova_area=[]
        for i in range(0,len(lista_num_bacia)):
            for j in range(0,len(lista_bacias)):
                if lista_bacias[i]==lista_num_bacia[j]:
                    lista_nova_area.append(lista_area[j])

        var_escreve_file='\n[SUBCATCHMENTS]\n'
        for i in range(0,len(lista_bacias)):
            var_escreve_file+=f's_{lista_bacias[i]}\t1\t{lista_no_sep[i]}\t{lista_nova_area[i]}\t0.1\t500\t0.5\t0\n'

        var_escreve_file+='\n[SUBAREAS]\n'
        for i in range(0,len(lista_bacias)):
            var_escreve_file+=f's_{lista_bacias[i]}\t0.01\t0.1\t0.05\t0.05\t25\tOUTLET\n' 

        var_escreve_file+='\n[INFILTRATION]\n'
        for i in range(0,len(lista_bacias)):
            var_escreve_file+=f's_{lista_bacias[i]}\t3.5\t0.5\t0.25\n'



###5 parte####
#Recebe arquivo csv para leitura
        tabelaTrechos=r"C:\Users\leona\OneDrive\Área de Trabalho\IC_UFSJ\ANEW_PROJ\TrechoCSV-mod.csv" 
        arquivo_Trechos = open(tabelaTrechos, 'r')
        lista_trechos = []
        lista_trechos=function_ret_carac(arquivo_Trechos)

        for i in range(0,len(lista_trechos)):
            del lista_trechos[i][0]

        lista_id_trechos=[]
        for i in range(0,len(lista_trechos)):
            lista_id_trechos.append(lista_trechos[i][0])
###6 parte####
#Recebe arquivo csv para leitura
        tabelaNOS=r"C:\Users\leona\OneDrive\Área de Trabalho\IC_UFSJ\ANEW_PROJ\PontosCSV_L-mod.csv" 
        arquivo_Nos_2 = open(tabelaNOS, 'r')
        lista_tab_Nos2 = []
        lista_tab_Nos2=function_ret_carac(arquivo_Nos_2)

        for i in range(0,len(lista_tab_Nos2)):
            del lista_tab_Nos2[i][0]
            del lista_tab_Nos2[i][1]

  
        lista_cond=[]
        for i in range(0,len(lista_tab_Nos2)):
            lista_cond.append(lista_tab_Nos2[i][0])

        lista1=[]
        for i in range(0,len(lista_trechos)):
            for j in range(0,len(lista_tab_Nos2)):
                if lista_trechos[i][1]==lista_tab_Nos2[j][1] and lista_trechos[i][2]==lista_tab_Nos2[j][2]:
                    lista1.append(lista_trechos[i][0]+" "+lista_tab_Nos2[j][0])
           #lista1.append(lista_tab_Nos2[j][0])
        lista2=[]
        for i in range(0,len(lista_trechos)):
            for j in range(0,len(lista_tab_Nos2)):           
                if lista_trechos[i][3]==lista_tab_Nos2[j][1] and lista_trechos[i][4]==lista_tab_Nos2[j][2]:    
                    lista2.append(lista_tab_Nos2[j][0]+" "+lista_trechos[i][5])
                    #lista2.append(lista_trechos[i][5])


        lista_final=[]
        for i in range(0,len(lista1)):
            lista_final.append(lista1[i]+" "+lista2[i])




        lista_final_modifi=[]
        for i in range(0,len(lista_final)):
            lista_final_modifi.append(lista_final[i].split())

        lista_exultorio=[]
        acm=0
        for i in range(0,len(lista_final_modifi)):
           acm=0
           for j in range(0,len(lista_final_modifi)):
               if lista_final_modifi[i][1]==lista_final_modifi[j][1] or lista_final_modifi[i][1]==lista_final_modifi[j][2]:
                   acm=acm+1

           if acm==1:
               lista_exultorio.append(lista_final_modifi[i][1])
        acm1=0
        for i in range(0,len(lista_final_modifi)):
            acm1=0
            for j in range(0,len(lista_final_modifi)):
                if lista_final_modifi[i][2]==lista_final_modifi[j][1] or lista_final_modifi[i][2]==lista_final_modifi[j][2]:
                    acm1=acm1+1

            if acm1==1:
                lista_exultorio.append(lista_final_modifi[i][2])

###4 parte####
#Recebe arquivo csv para leitura
        tabelaNOS=r"C:\Users\leona\OneDrive\Área de Trabalho\IC_UFSJ\ANEW_PROJ\PontosCSV_L-mod.csv" 
        arquivo_Nos_1 = open(tabelaNOS, 'r')
        lista_tab_Nos1 = []
        lista_tab_Nos1=function_ret_carac(arquivo_Nos_1)

        for i in range(0,len(lista_tab_Nos1)):
            del lista_tab_Nos1[i][0]

        for i in range(0,len(lista_tab_Nos1)):
            for j in range(0,len(lista_tab_Nos1)):
                if float(lista_tab_Nos1[i][1])<float(lista_tab_Nos1[j][1]):
                    var_chave=i   

        lista_num_no=[]
        for i in range(0,len(lista_tab_Nos1)):
            lista_num_no.append(lista_tab_Nos1[i][0])


        lista_alt=[]
        for i in range(0,len(lista_tab_Nos1)):
            lista_alt.append(lista_tab_Nos1[i][1])


        lista_x=[]
        for i in range(0,len(lista_tab_Nos1)):
           lista_x.append(lista_tab_Nos1[i][2])


        lista_y=[]
        for i in range(0,len(lista_tab_Nos1)):
            lista_y.append(lista_tab_Nos1[i][3])     



        new_lista=[]
        for i in range(0,len(lista_num_no)):
            var_boleana=False
            for j in range(0,len(lista_exultorio)):
                if lista_num_no[i] == lista_exultorio[j]:
                   var_boleana=True
  
            if var_boleana==False:
                new_lista.append(lista_num_no[i])

        lista_exultorio.sort()    
        var_escreve_file+='\n[JUNCTIONS]\n'
        for i in range(0,len(lista_num_no)):
            for j in range(0,len(new_lista)):
                if lista_num_no[i]==new_lista[j]:
                    var_escreve_file+=f'{lista_num_no[i]}\t{lista_alt[i]}\t1.25\t0\t0\t0\n'

        var_escreve_file+='\n[OUTFALLS]\n'
        for i in range(0,len(lista_num_no)):
            for j in range(0,len(lista_exultorio)):
                if lista_num_no[i]==lista_exultorio[j]:
                    var_escreve_file+=f'{lista_num_no[i]}\t{lista_alt[i]}\tFREE\tNO\n'   
  

        var_escreve_file+='\n[CONDUITS]\n'
        for i in range(0,len(lista_final_modifi)):
            var_escreve_file+=f'{lista_final_modifi[i][0]}\t{lista_final_modifi[i][1]}\t{lista_final_modifi[i][2]}\t{lista_final_modifi[i][3]}\t0.01\t0\t0\t0\t0\n'


        var_escreve_file+='\n[XSECTIONS]\n'
        for i in range(0,len(lista_final_modifi)):
            var_escreve_file+=f'{lista_final_modifi[i][0]}\tCIRCULAR\t.305\t0\t0\t0\t1\n'

        var_escreve_file+='\n[COORDINATES]\n'
        for i in range(0,len(lista_tab_Nos2)):
                var_escreve_file+=f'{lista_tab_Nos2[i][0]}\t{lista_tab_Nos2[i][1]}\t{lista_tab_Nos2[i][2]}\n'


        pontosDesenho=r"C:\Users\leona\OneDrive\Área de Trabalho\IC_UFSJ\ANEW_PROJ\desenho_subBacia.csv"
        manipulador3 = open(pontosDesenho,'r')
        desenho_subBacia = []
        for l in manipulador3:
            l_strip = l.strip()
            l_limpo = l_strip.replace('"','')
            l_dividido = l_limpo.split(',')
            desenho_subBacia.append(l_dividido)
        del desenho_subBacia[0]

        nomes_das_subBacias = []
        for i in desenho_subBacia:
            if(not(i[0] in nomes_das_subBacias)):
               nomes_das_subBacias.append(i[0])

        ordem_para_desenho = []
        temp = []
        cont = 0
        for n in nomes_das_subBacias:
            for i in desenho_subBacia:
                if (i[0] == n):
                    temp.append(i[:])

            while(len(temp)>0):
                for i in temp:
                    if(i[1] == str(cont)): #a segunda coluna contem a ordem correta para fazer o desenho
                        ordem_para_desenho.append(i[:])
                        del temp[(temp.index(i))]
                        #print(temp)
                cont += 1
            temp.clear()
            cont = 0
        var_escreve_file+='\n[Polygons]\n'
        for i in ordem_para_desenho:
            var_escreve_file+=f's_{i[0]}\t{i[2]}\t{i[3]}\n'  


        diretorio_aq_swmm=r"C:\Users\leona\OneDrive\Área de Trabalho\IC_UFSJ\ANEW_PROJ\Bacias_swmm.txt"
        arquivo_SWMM = open(diretorio_aq_swmm,'w')
        arquivo_SWMM.write(var_escreve_file)
        arquivo_SWMM.close()  
          
          
          
          
          
          
          
        
        return results    
        
           
    def name(self):
        return 'Alg Rede e Sub Bacias'
    def name(self):
        return 'Alg Rede e Sub Bacias'

    def displayName(self):
        return 'Alg Rede e Sub Bacias'

    def group(self):
        return 'Rede e Sub Bacias'

    def groupId(self):
        return 'Rede e Sub Bacias'

    def createInstance(self):
        return AlgRedeESubBacias()
  
        
        
        
        
        
        
       

   