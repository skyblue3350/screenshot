# -*- encoding: utf-8 -*-

import datetime
import time
import sys
import os

import sip
sip.setapi("QString", 2)

from PyQt4 import QtGui, QtCore

class ScreenShot(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent=parent)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.settings = QtCore.QSettings("./settings.ini", QtCore.QSettings.IniFormat)
		self.settings.beginGroup("setting")

		if self.settings.value("path", None).isNull():
			self.path = QtGui.QFileDialog.getExistingDirectory(self, u"画像保存先", ".", QtGui.QFileDialog.ShowDirsOnly)
			if self.path == "":
				sys.exit()
				#QtGui.qApp.quit()
		else:
			self.path = "./"

		self.path = self.settings.value("path", self.path).toString()
		self.ext  = self.settings.value("ext",  "png").toString()
		self.openFolder = self.settings.value("openFolder", True).toBool()
		self.settings.endGroup()

	def closeEvent(self, event):
		self.settings.beginGroup("setting")
		self.settings.setValue("path", self.path)
		self.settings.setValue("ext", self.ext)
		self.settings.setValue("openFolder", self.openFolder)
		self.settings.endGroup()

	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Escape:
			QtGui.qApp.quit()

	def shot(self):
		self.show()
		desktop = QtGui.QApplication.desktop()
		size = desktop.screen().rect()
		self.pixmap = QtGui.QPixmap.grabWindow(desktop.winId(), desktop.x(), desktop.y(), size.width(), size.height() )
		self.move(desktop.x(),desktop.y())
		self.resize(size.width(), size.height())

		self.start = QtCore.QPoint(0, 0)
		self.end   = QtCore.QPoint(0, 0)

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		painter.setPen(QtCore.Qt.NoPen)

		screenRect = QtGui.QApplication.desktop().screen(0).rect()
		painter.drawPixmap(0, 0, screenRect.width(), screenRect.height(), self.pixmap)

		path = QtGui.QPainterPath()
		path.addRect(QtCore.QRectF(screenRect))
		path.addRoundRect(QtCore.QRectF(self.start, self.end), 0, 0)

		painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 90)))
		painter.drawPath(path)

	def mouseMoveEvent(self, event):
		self.end = event.pos()
		self.repaint()

	def mousePressEvent(self, event):
		self.start = event.pos()

	def mouseReleaseEvent(self, event):
		self.end = event.pos()

		start = QtCore.QPoint()
		end  = QtCore.QPoint()
		start.setX(min(self.start, self.end, key=lambda p: p.x()).x())
		start.setY(min(self.start, self.end, key=lambda p: p.y()).y())
		end.setX(max(self.start, self.end, key=lambda p: p.x()).x())
		end.setY(max(self.start, self.end, key=lambda p: p.y()).y())
		self.start, self.end = start, end

		self.takeScreenShot()

	def takeScreenShot(self):
		pixmap = self.pixmap.copy(QtCore.QRect(self.start, self.end))
		filename = "%s.%s" % (datetime.datetime.now().strftime("%Y年%m月%d日%H時%M分%S秒").decode("utf-8"), self.ext)
		path = (self.path+os.sep+filename)
		pixmap.save(path)
		self.close()

		if self.openFolder:
			#Platform Windows
			cmd  = ("explorer /select,\"%s\" " % ( path)).encode("cp932")
			os.system( cmd )


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	viewer = ScreenShot()
	viewer.shot()
	sys.exit(app.exec_())
