# -*- encoding: utf-8 -*-

import miniconf
import datetime
import time
import sys
import os

import sip
sip.setapi('QString', 2)
from PyQt4 import QtGui,QtCore

class ScreenShot(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent=parent)
		#枠を除く
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

		#設定ファイル読み込み
		try:
			f = open("setting.cfg", "r")
			self.setting = miniconf.load(f.read())
			#要素不足なら例外
			for i in ["ext", "path"]:
				if not (i in self.setting):
					raise IOError
		except IOError:
			QtGui.QMessageBox.warning(self, u"エラー", u"設定ファイル（setting.cfg）を開くことが出来ませんでした。\n初期設定を行います。")
			try:
				path = QtGui.QFileDialog.getExistingDirectory(self, u"画像保存先", ".", QtGui.QFileDialog.ShowDirsOnly)
				if path == "":
					sys.exit()
				ext, ok = QtGui.QInputDialog.getText(self, u"拡張子", u"保存時の拡張子（jpg or png）：")
				if not (ext == "jpg" or ext == "png"):
					sys.exit()
				self.setting = {
					"path": path,
					"ext" : ext,
					"openFolder": True,
				}
				data = miniconf.dump(self.setting)
				f = open("setting.cfg", "w")
				f.write(data)
			except IOError:
				QtGui.QMessageBox.warning(self, u"エラー", u"setting.cfgに書き込む権限がありません")
				sys.exit()
			else:
				f.close()
				time.sleep(0.5)
		else:
			f.close()


	def shot(self):
		#デスクトップの情報収集
		desktop = QtGui.QApplication.desktop()
		size = desktop.screen().rect()
		self.pixmap = QtGui.QPixmap.grabWindow(desktop.winId(), desktop.x(), desktop.y(), size.width(), size.height() )
		self.move(desktop.x(),desktop.y())
		self.resize(size.width(), size.height())

		#マウスの開始地点と終了地点
		self.start = QtCore.QPoint(0, 0)
		self.end   = QtCore.QPoint(0, 0)

		#表示
		self.show()

	def keyPressEvent(self, event):
		#ESCで終了
		if event.key() == QtCore.Qt.Key_Escape:
			self.close()

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
		self.takeScreenShot()

	def takeScreenShot(self):
		pixmap = self.pixmap.copy(QtCore.QRect(self.start, self.end))
		pixmap.save(u"%s\\%s.%s" % (self.setting["path"], datetime.datetime.now().strftime("%Y年%m月%d日%H時%M分%S秒").decode("utf-8"), self.setting["ext"] ))
		self.close()
		if self.setting["openFolder"]: os.system( ("explorer %s" % self.setting["path"]).encode("cp932") )

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	viewer = ScreenShot()
	viewer.shot()
	sys.exit(app.exec_())
