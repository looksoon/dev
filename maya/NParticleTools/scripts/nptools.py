import sys
import os
import random
import json
import pymel.core as pc
from PySide import QtGui, QtCore

import lib.qt as qt

import maya.lib.qt as mayaqt

class UIParent(object):
    def __init__(self, uiFile):

        ui = os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/ui/' + uiFile + '.ui')
        self.file = qt.loadUiType(ui)


    def ui(self):
        return self.file

base, form = UIParent('nptools').ui()
class NPTools(base, form):
    def __init__(self, parent=mayaqt.getMayaWindow()):
        super(NPTools, self).__init__(parent)
        self.setupUi(self)

        self.nparticle = None
        self.sequence = None
        self.currentUnit = Get_currentUnit()

        self.init_ui()

    def init_ui(self):

        self.btn_pick.clicked.connect(self.pick_nparticle)
        self.btn_select.clicked.connect(self.select_nparticle)
        self.com_shape.currentIndexChanged.connect(self.apply_shape)
        self.btn_emRefresh.clicked.connect(self.update_emitters)
        self.btn_randomSeeds.clicked.connect(self.apply_emitSeed)
        self.btn_selCurrentEmitter.clicked.connect(lambda: self.select_emitter("current"))
        self.btn_selAllEmitters.clicked.connect(lambda: self.select_emitter("all"))
        self.bnt_insRefresh.clicked.connect(self.update_instancers)
        self.btn_insSelect.clicked.connect(self.select_instancer)

        self.btn_applyStaticSeeds.clicked.connect(self.apply_seedAndLifespan)
        self.btn_applyGoalExp.clicked.connect(self.apply_goal)

        self.btn_applyScale.clicked.connect(self.apply_insScale)
        self.btn_applyIndex.clicked.connect(self.apply_insRandomIndex)
        self.btn_applySpin.clicked.connect(self.apply_insSpinType)

        self.btn_pickTrailPar.clicked.connect(self.pick_trail)
        self.btn_applyTrailEffect.clicked.connect(self.apply_trail)

        self.btn_pickTextures.clicked.connect(self.pick_seqTextures)
        self.btn_applyRenderSettings.clicked.connect(self.apply_renderSettings)


    def select_emitter(self, selType):
        num = self.com_emitters.count()

        if num > 0:
            ems = [self.com_emitters.currentText()]

            if selType == "all":
                ems =[]
                for i in range(num):
                    ems.append(self.com_emitters.itemText(i))

            pc.select(ems, r=True)


    def update_emitters(self):
        emitters = self.nparticle.get_emitters()

        if len(emitters):
            emList = [str(em) for em in emitters]
            self.com_emitters.clear()
            self.com_emitters.addItems(emList)


    def update_instancers(self):
        instancers = self.nparticle.get_instancers()

        if len(instancers):
            insList = [str(ins) for ins in instancers]
            self.com_instancers.clear()
            self.com_instancers.addItems(insList)


    def apply_shape(self):
        index = self.com_shape.currentIndex()
        self.nparticle.set_shape(index)


    def apply_emitSeed(self):

        self.nparticle.set_randomSeeds()


    def apply_seedAndLifespan(self):


        self.nparticle.apply_func(func="staticSeed",
                                  stats=(self.chk_staticSeeds.isChecked(), False, False),
                                  crt=(),
                                  rbd=(),
                                  rad=())


        self.nparticle.apply_func(func="randomLifespan",
                                  stats=(self.chk_lifespanPP.isChecked(), False, False),
                                  crt=(self.dspn_lifeMin.value(), self.dspn_lifeMax.value(), self.dspn_lifeMult.value()),
                                  rbd=(),
                                  rad=())

        if self.chk_lifespanPP.isChecked():
            self.nparticle.set_attr(lifespanMode=3)


    def apply_goal(self):

        if len(self.nparticle.pynode().goalGeometry.elements()) > 0:
            # self.nparticle.apply_func(func="flowingOn",
            #                     stats=self.chk_stickOn.isChecked(),
            #                     crt=(),
            #                     rbd=(),
            #                     rad=())


            direct = self.com_flowingOnDir.currentText()
            dir = ">"

            if direct[0] == "-":
                dir = "<"
            goalObj = pc.listConnections("%s.goalGeometry[0]" % self.nparticle.name(), d=True, sh=True)[0]
            uv = Get_UVBB(goalObj, direct)
            self.nparticle.apply_func(func="killedWhenAge",
                                stats=(False,
                                       self.chk_stickOn.isChecked() and self.chk_killParWhenEdge.isChecked(),
                                       False),
                                crt=(),
                                rbd=(direct[1], dir, uv),
                                rad=())


            self.nparticle.apply_func(func="flowingOn",
                                  stats=(self.chk_stickOn.isChecked(),
                                         self.chk_stickOn.isChecked() and self.chk_flowingOn.isChecked(),
                                         False),
                                  crt=(self.dspn_speedMin.value(), self.dspn_speedMax.value(), self.dspn_speedMult.value()),
                                  rbd=(direct[1], direct[0]),
                                  rad=())


    def apply_insScale(self):

        currentIns = self.com_instancers.currentText()


        if not self.chk_randScale.isChecked():

            self.nparticle.set_insAttr(name=currentIns, scale="")
            # self.nparticle.set_parAttr(radiusScaleInput=0)


        else:

            self.nparticle.set_insAttr(name=currentIns, scale="radiusPP")
            self.nparticle.set_radiusAttr(radius=self.dspin_scaleMult.value(),
                                          radiusScale=([0, 1, 1], [0.2, 0.3, 1], [1, 0.1, 1]),
                                          radiusScaleInput=6,
                                          radiusScaleInputMax=1,
                                          radiusScaleRandomize=0
                                          )


    def apply_insRandomIndex(self):


        currentIns = self.com_instancers.currentText()

        crt_status = self.chk_randIndex.isChecked()
        rbd_status = True
        if self.chk_randIndex.isChecked():
            if not self.chk_aniByFrame.isChecked():
                rbd_status = False
        else:
            rbd_status = False


        if len(currentIns):

            self.nparticle.apply_func(func="insRandomIndex",
                                      stats=(crt_status, rbd_status, False),
                                      crt=(self.nparticle.get_instanceCount(currentIns)),
                                      rbd=(self.nparticle.get_instanceCount(currentIns)),
                                      rad=())


            if not self.chk_randIndex.isChecked() and not self.chk_aniByFrame.isChecked():

                self.nparticle.set_insAttr(name=currentIns, objectIndex="")


            else:

                self.nparticle.set_insAttr(name=currentIns, objectIndex="c_indexPP")


    def apply_insSpinType(self):

        spinType = self.com_rotationType.currentIndex()


        if spinType == 0:

            self.apply_insSpin()


        elif spinType == 1:
            self.apply_insAimDir()


    def apply_insSpin(self):

        currentIns = self.com_instancers.currentText()

        crt_status = self.chk_spin.isChecked()
        rbd_status = True
        if self.chk_spin.isChecked():
            if not self.chk_spinAni.isChecked():
                rbd_status = False
        else:
            rbd_status = False

        if len(currentIns):

            self.nparticle.apply_func(func="insRandomSpin",
                                      stats=(crt_status, rbd_status, False),
                                      crt=(self.dspin_spinMin.value(), self.dspin_spinMax.value(), self.dspin_spinMult.value()),
                                      rbd=(),
                                      rad=())


            if not self.chk_spin.isChecked():

                self.nparticle.set_insAttr(name=currentIns, rotation="")


            else:
                 self.nparticle.set_insAttr(name=currentIns, rotation="c_spinPP")


    def apply_insAimDir(self):

        currentIns = self.com_instancers.currentText()

        crt_status = self.chk_aimVel.isChecked()
        rbd_status = True
        if self.chk_aimVel.isChecked():
            if not self.chk_aimAnVel.isChecked():
                rbd_status = False
        else:
            rbd_status = False

        aim = [1, 0, 0]
        a = "0"
        b = "sin(time * c_spinSpeedPP + id)"
        c = "cos(time * c_spinSpeedPP + id)"
        aimUp = [a, b, c]
        if self.com_aimAxis.currentIndex() == 1:
            aim = [0, 1, 0]
            aimUp = [b, a, c]
        elif self.com_aimAxis.currentIndex() == 2:
            aim = [0, 0, 1]
            aimUp = [b, c, a]
        elif self.com_aimAxis.currentIndex() == 3:
            aim = [-1, 0, 0]
        elif self.com_aimAxis.currentIndex() == 4:
            aim = [0, -1, 0]
            aimUp = [b, a, c]
        elif self.com_aimAxis.currentIndex() == 5:
            aim = [0, 0, -1]
            aimUp = [b, c, a]

        aim.extend([self.dspin_spinMin.value(), self.dspin_spinMax.value(), self.dspin_spinMult.value()])
        aim.extend(aimUp)


        if len(currentIns):

            self.nparticle.apply_func(func="insAimDirection",
                                      stats=(crt_status, rbd_status, False),
                                      crt=(aim[0],aim[1],aim[2],aim[3],aim[4],aim[5],aim[6],aim[7],aim[8]),
                                      rbd=(aim[6], aim[7], aim[8]),
                                      rad=())


            if not self.chk_aimVel.isChecked():

                self.nparticle.set_insAttr(name=currentIns, aimDirection="")
                self.nparticle.set_insAttr(name=currentIns, aimAxis="")
                self.nparticle.set_insAttr(name=currentIns, aimUpAxis="")


            else:

                self.nparticle.set_insAttr(name=currentIns, rotation="")
                self.nparticle.set_insAttr(name=currentIns, aimDirection="velocity")
                self.nparticle.set_insAttr(name=currentIns, aimAxis="c_aimAxisPP")
                self.nparticle.set_insAttr(name=currentIns, aimUpAxis="c_aimUpAxisPP")


    def apply_trail(self):

        func_list = [("particleTrailAn",
                      True,
                      (self.lne_listTrail.text(), self.spn_dividNumber.value(), self.currentUnit))]
        self.nparticle.apply_func(func="trail",
                                  stats=(False, True, True),
                                  crt=(),
                                  rbd=(),
                                  rad=(self.lne_listTrail.text(), self.spn_dividNumber.value(), self.currentUnit))


    def pick_nparticle(self):

        objs = pc.ls(sl=True)


        if len(objs):

            shape = Get_shape(objs[0], "nParticle")


            if shape:

                self.nparticle = NParticle(shape)
                self.lne_list.setText(str(shape))

                self.update_emitters()
                self.update_instancers()


    def pick_trail(self):

        objs = pc.ls(sl=True)


        if len(objs):

            shape = Get_shape(objs[0], "nParticle")


            if shape and shape != self.nparticle:

                self.lne_listTrail.setText(str(shape))
                shape.collide.set(0)
                shape.selfCollide.set(0)
                shape.ignoreSolverGravity.set(1)


    def pick_seqTextures(self):

        files = QtGui.QFileDialog.getOpenFileNames(self.btn_applyRenderSettings,
                                                   "Pick the sequence of textures:",
                                                   "/home/21cores/DeltaStudio/maya/public/source/sprite_test",
                                                   "Image Files(*.png *.tif *.tga *.iff)")
        self.sequence = files[0]
        self.lne_seqLength.setText("%d" % len(self.sequence))


    def apply_renderSettings(self):

        options = {
            "sequence": self.sequence,
            "use_as_color": self.chk_useColor.isChecked(),
            "use_rgbPP": self.chk_useRGB.isChecked(),
            "use_opacityPP": self.chk_useOpacity.isChecked(),
            "use_twistPP": self.chk_useTwist.isChecked()
        }

        if self.tab_npType.currentIndex() == 0:

            self.nparticle.apply_spriteShader(options)


    def select_nparticle(self):

        nparticle = self.lne_list.text()


        if nparticle:

            pc.select(pc.PyNode(nparticle), r=True)


    def select_instancer(self):

        ins = self.com_instancers.currentText()


        if pc.objExists(ins):

            pc.select(ins, r=True)



class NParticle(object):

    def __init__(self, nparticle):

        self.nparticle = nparticle

        self.exp_json = Load_dict()
        self.exp_par = self.read_exp()


    def name(self):

        return self.nparticle.name()


    def pynode(self):

        return self.nparticle

    def set_shape(self, shapeID):

        index = shapeID


        if index == 0:

            self.nparticle.particleRenderType.set(3)
            self.nparticle.aiRadiusMultiplier.set(0)


        elif index == 1:

            self.nparticle.particleRenderType.set(3)
            self.nparticle.aiRadiusMultiplier.set(1)


        elif index == 2:

            self.nparticle.particleRenderType.set(0)
            self.nparticle.aiRadiusMultiplier.set(1)


        elif index == 3:

            self.nparticle.particleRenderType.set(4)
            self.nparticle.aiRadiusMultiplier.set(1)


        elif index == 4:

            self.nparticle.particleRenderType.set(5)
            self.nparticle.aiRadiusMultiplier.set(1)


    def get_emitters(self):

        return pc.listConnections(self.nparticle.newParticles, d=True)


    def get_instancers(self):

        return pc.listConnections(self.nparticle.newParticles.instanceData, s=True)


    def get_instanceCount(self, txt):

        return len(pc.PyNode(txt).inputHierarchy.elements())


    def apply_emitSeed(self):

        seedsAttr = self.nparticle.seed.elements()


        for attr in seedsAttr:

            pc.Attribute(self.nparticle + "." + attr).set(random.uniform(0, 50))


    def set_attr(self, **kwargs):

        for key, value in kwargs.items():

            pc.Attribute("%s.%s" %(self.nparticle.name(),  key)).set(value)


    def set_insAttr(self, **kwargs):

        pc.particleInstancer(self.nparticle, e=True, **kwargs)


    def set_radiusAttr(self, **kwargs):

        self.clearMutiAttr("radiusScale")


        for key, value in kwargs.items():

            if key != "radiusScale":

                pc.Attribute("%s.%s" % (self.nparticle.name(), key)).set(value)


            else:

                for i in range(len(value)):

                    pc.Attribute("%s.%s[%d].radiusScale_Position" %(self.nparticle.name(), key, i)).set(value[i][0])

                    pc.Attribute("%s.%s[%d].radiusScale_FloatValue" % (self.nparticle.name(), key, i)).set(value[i][1])

                    pc.Attribute("%s.%s[%d].radiusScale_Interp" % (self.nparticle.name(), key, i)).set(value[i][2])


    def clearMutiAttr(self, attr):

        multies = pc.listAttr(self.nparticle, m=True, st=attr)


        for i in range(len(multies)-1, 0, -1):

            pc.removeMultiInstance(pc.Attribute("%s.%s" % (self.nparticle.name(), multies[i])))


    def read_exp(self):

        result = {}

        expressions = {"crt": pc.dynExpression(self.nparticle, q=True, c=True),
                       "rbd": pc.dynExpression(self.nparticle, q=True, rbd=True),
                       "rad": pc.dynExpression(self.nparticle, q=True, rad=True)}


        for key in self.exp_json.keys():

            tag_begin = "//__%s_Start_Tag__\n" % key
            tag_end = "//__%s_End_Tag__" % key


            for ek, value in expressions.items():

                pos_start = value.find(tag_begin)
                pos_end = value.find(tag_end)


                if pos_start != -1 and pos_end != -1:

                    result[key] = {}
                    result[key]["attrs"] = self.exp_json[key]["attrs"]
                    result[key]["exp"] = {"crt": "", "rbd": "", "rad": ""}


            for ek, value in expressions.items():

                pos_start = value.find(tag_begin)
                pos_end = value.find(tag_end)


                if pos_start != -1 and pos_end != -1:

                    result[key]["exp"][ek] = value[pos_start:pos_end+len(tag_end)]


        # for key, value in result.items():
        #     print key
        #     for k, v in value.items():
        #         print k
        #         print v
        return result


    def write_exp(self):

        tmp = self.exp_par

        crt_exp = rbd_exp = rad_exp = "\n"

        for key in ["staticSeed", "randomLifespan", "flowingOn"]:


            if key in tmp.keys():


                if "crt" in tmp[key]["exp"].keys():

                    crt_exp += "\n" + tmp[key]["exp"]["crt"]
                    tmp[key]["exp"].pop("crt")


                if "rbd" in tmp[key]["exp"].keys():

                    rbd_exp += "\n" + tmp[key]["exp"]["rbd"]
                    tmp[key]["exp"].pop("rbd")


                if "rad" in tmp[key]["exp"].keys():

                    rad_exp += "\n" + tmp[key]["exp"]["rad"]
                    tmp[key]["exp"].pop("rad")



        for key, value in tmp.items():

            if "crt" in value["exp"].keys():

                crt_exp += "\n" + value["exp"]["crt"]


            if "rbd" in value["exp"].keys():

                rbd_exp += "\n" + value["exp"]["rbd"]


            if "rad" in value["exp"].keys():

                rad_exp += "\n" + value["exp"]["rad"]

        # print crt_exp
        pc.dynExpression(self.nparticle, s=crt_exp, c=True)
        pc.dynExpression(self.nparticle, s=rbd_exp, rbd=True)
        pc.dynExpression(self.nparticle, s=rad_exp, rad=True)




    def apply_func(self, **kwargs):

        # print self.exp_par.keys()
        # print func in self.exp_par.keys()

        func = kwargs["func"]
        status = kwargs["stats"]



        if func in self.exp_par.keys():


            if not status[0] and not status[2] and not status[2]:

                self.exp_par.pop(func)
                self.write_exp()
                self.update_attrs(func, False)


            else:


                if status[0]:

                    self.exp_par[func]["exp"]["crt"] = self.exp_json[func]["exp"]["crt"] % kwargs["crt"]


                else:

                    self.exp_par[func]["exp"]["crt"] = ""


                if status[1]:

                    self.exp_par[func]["exp"]["rbd"] = self.exp_json[func]["exp"]["rbd"] % kwargs["rbd"]


                else:

                    self.exp_par[func]["exp"]["rbd"] = ""


                if status[2]:

                    self.exp_par[func]["exp"]["rad"] = self.exp_json[func]["exp"]["rad"] % kwargs["rad"]


                else:

                    self.exp_par[func]["exp"]["rad"] = ""


                self.write_exp()


        else:

                self.exp_par[func] = {"attrs": self.exp_json[func]["attrs"], "exp": {}}


                if status[0]:

                    self.exp_par[func]["exp"]["crt"] = self.exp_json[func]["exp"]["crt"] % kwargs["crt"]


                if status[1]:

                    self.exp_par[func]["exp"]["rbd"] = self.exp_json[func]["exp"]["rbd"] % kwargs["rbd"]


                if status[2]:

                    self.exp_par[func]["exp"]["rad"] = self.exp_json[func]["exp"]["rad"] % kwargs["rad"]


                self.update_attrs(func, True)
                self.write_exp()

        self.exp_par = self.read_exp()

    def update_attrs(self, func, status):

        attrs = self.exp_json[func]["attrs"]


        if status:


            for attr, attrType in attrs.items():


                if not pc.attributeQuery(attr, node=self.nparticle.name(), exists=True):
                    pc.addAttr(self.nparticle.name(), ln=attr, dt=attrType)
                    pc.addAttr(self.nparticle.name(), ln=("%s0" % attr), dt=attrType)


        else:


            for attr, attrType in attrs.items():


                if pc.attributeQuery(attr, node=self.nparticle.name(), exists=True):


                    if len(pc.listConnections("%s.%s" % (str(self.nparticle), attr))) == 0:

                        pc.deleteAttr(self.nparticle.name(), at=attr)
                        pc.deleteAttr(self.nparticle.name(), at=("%s0" % attr))


                    else:

                        pc.warning("Can't remove Attribute:%s(Function:%s), which is being used." % (attr, func))




    # def write_exp(self):
    #     return

    def apply_spriteShader(self, options):
        self.nparticle.aiOpaque.set(False)

        # Append these three attribute to nparticle's aiExportAttributes as Default
        parAttr_default = ["rgbPP", "opacityPP", "twistPP"]
        parAttr_export = self.nparticle.aiExportAttributes.get().split()
        for attr in parAttr_default:
            if attr not in parAttr_export:
                parAttr_export.append(attr)

        self.nparticle.aiExportAttributes.set(" ".join(parAttr_export))


        pre_name = str(self.nparticle)
        ramp_color_name = "%s_color_ramp" %pre_name
        ramp_opacity_name = "%s_opacity_ramp" % pre_name
        ramp_color = None
        ramp_opacity=None

        if len(options["sequence"]):
            shader, shader_group = pc.createSurfaceShader("aiStandard", name="%s_shader" %pre_name)

            aiUserDataFloat = pc.shadingNode("aiUserDataFloat", asShader=True)
            aiUserDataFloat.floatAttrName.set("spriteNumPP")

            ramp_opacity = pc.shadingNode("ramp", asTexture=True, name=ramp_opacity_name)
            ramp_opacity.interpolation.set(0)
            ramp_opacity.colorEntryList[0].position.set(0)
            ramp_opacity.outColor.connect(shader.opacity, f=True)
            aiUserDataFloat.outValue.connect(ramp_opacity.uvCoord.vCoord, f=True)

            if options["use_as_color"]:
                ramp_color = pc.shadingNode("ramp", asTexture=True, name=ramp_color_name)
                ramp_color.interpolation.set(0)
                ramp_color.colorEntryList[0].position.set(0)
                ramp_color.outColor.connect(shader.color, f=True)
                aiUserDataFloat.outValue.connect(ramp_color.uvCoord.vCoord, f=True)



            texPlacement = pc.shadingNode("place2dTexture", asUtility=True)
            texPlacement.wrapU.set(0)
            texPlacement.wrapV.set(0)
            for i in range(len(options["sequence"])):
                texFile = pc.shadingNode("file", asTexture=True)
                texFile.fileTextureName.set(options["sequence"][i])
                ConnectPlace2DTexture(texFile, texPlacement)
                texFile.outTransparency.connect(ramp_opacity.colorEntryList[i].color, f=True)
                ramp_opacity.colorEntryList[i].position.set(float(i)/len(options["sequence"]))
                if options["use_as_color"]:
                    texFile.outColor.connect(ramp_color.colorEntryList[i].color, f=True)
                    ramp_color.colorEntryList[i].position.set(float(i) / len(options["sequence"]))

            # If to use rgbPP
            if options["use_rgbPP"]:
                aiUserDataColor = pc.shadingNode("aiUserDataColor", asShader=True)
                aiUserDataColor.colorAttrName.set("rgbPP")

                # If ramp_color had connected to shader's color
                if ramp_color:
                    aiUserDataColor.outColor.connect(ramp_color.colorGain, f=True)
                else:
                    aiUserDataColor.outColor.connect(shader.color, f=True)


            # If to use opacityPP
            if options["use_opacityPP"]:
                aiUserDataOpacity = pc.shadingNode("aiUserDataColor", asShader=True)
                aiUserDataOpacity.colorAttrName.set("opacityPP")

                # If ramp_opacity had connected to shader's opacity
                if ramp_opacity:
                    aiUserDataOpacity.outColor.connect(ramp_opacity.colorGain, f=True)
                else:
                    aiUserDataOpacity.outColor.connect(shader.opacity, f=True)


            # If to use spriteTwistPP
            if options["use_twistPP"]:
                aiUserDataTwist = pc.shadingNode("aiUserDataFloat", asShader=True)
                aiUserDataTwist.floatAttrName.set("spriteTwistPP")

                aiUserDataTwist.message.connect(texPlacement.rotateFrame, f=True)


            pc.sets(shader_group, forceElement=self.nparticle)




def Load_dict():
    '''
    Read the preset expression from json's file.
    and add Tag for every functions.

    @arguments:

    @return:
     return a directory with Tag
    '''
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expression/expression.json")


    with open(full_path) as jFile:
        data = json.load(jFile)

        for key in data.keys():


            for exp_type, exp_str in data[key]["exp"].items():


                if exp_str:

                    tmp = "//__%s_Start_Tag__\n%s\n//__%s_End_Tag__\n" % (key, exp_str, key)
                    data[key]["exp"][exp_type] = tmp


        # print data
        return data


def Get_currentUnit():
    result = 0

    currentUnit = pc.currentUnit(q=True, time=True)
    if currentUnit == "game":
        result = 15
    elif currentUnit == "film":
        result = 24
    elif currentUnit == "pal":
        result = 25
    elif currentUnit == "ntsc":
        result = 30
    elif currentUnit == "show":
        result = 48
    elif currentUnit == "palf":
        result = 50
    elif currentUnit == "ntscf":
        result = 60

    return result


def ConnectPlace2DTexture(tex, place):
    place.coverage.connect(tex.coverage, f=True)
    place.translateFrame.connect(tex.translateFrame, f=True)
    place.rotateFrame.connect(tex.rotateFrame, f=True)
    place.mirrorU.connect(tex.mirrorU, f=True)
    place.mirrorV.connect(tex.mirrorV, f=True)
    place.stagger.connect(tex.stagger, f=True)
    place.wrapU.connect(tex.wrapU, f=True)
    place.wrapV.connect(tex.wrapV, f=True)
    place.offset.connect(tex.offset, f=True)
    place.rotateUV.connect(tex.rotateUV, f=True)
    place.noiseUV.connect(tex.noiseUV, f=True)
    place.vertexUvOne.connect(tex.vertexUvOne, f=True)
    place.vertexUvTwo.connect(tex.vertexUvTwo, f=True)
    place.vertexUvThree.connect(tex.vertexUvThree, f=True)
    place.vertexCameraOne.connect(tex.vertexCameraOne, f=True)
    place.outUV.connect(tex.uv, f=True)
    place.outUvFilterSize.connect(tex.uvFilterSize, f=True)

def Get_UVBB(obj, uv):
    uvbb = pc.polyEvaluate(obj, boundingBox2d=True)
    if uv == "+U":
        return uvbb[0][1]
    elif uv == "-U":
        return uvbb[0][0]
    elif uv == "+V":
        return uvbb[1][1]
    elif uv == "-V":
        return uvbb[1][0]

def Get_shape(obj, objType):
    shape = pc.ls(obj, dag=True, o=True, s=True)

    if len(shape):
        if shape[0].type() == objType:
            return shape[0]
    return None


def main():
    global mainWin
    try:
        mainWin.close()
    except:
        pass

    mainWin = NPTools()
    mainWin.show()
