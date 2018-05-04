# PYTHON 3
from PyQt5 import QtGui,QtCore,QtWidgets
import sys
if __name__=='__main__':
	import syntax
else:
	from . import syntax

FONT = {
	'size':10,
	'name':'DejaVu Sans Mono',
	'indent':4,
	}


def selectBlocks(self):
	i0 = self.selectionStart()
	i1 = self.selectionEnd()

	self.setPosition(self.document().findBlock(i0).position(),QtGui.QTextCursor.MoveAnchor)
	self.movePosition(QtGui.QTextCursor.Left,QtGui.QTextCursor.MoveAnchor)
	self.setPosition(i1,QtGui.QTextCursor.KeepAnchor)
	self.movePosition(QtGui.QTextCursor.EndOfBlock,QtGui.QTextCursor.KeepAnchor)
QtGui.QTextCursor.selectBlocks = selectBlocks



def yieldBlockInSelection_WW(self,direction=1):
	"""
	- direction : if positive, then will go forward otherwise, it will go
			backward.
	"""
	pos1=self.selectionStart()
	pos2=self.selectionEnd ()

	startCursor=QtGui.QTextCursor(self)
	endCursor=QtGui.QTextCursor(self)
	startCursor.setPosition(pos1)
	endCursor  .setPosition(pos2)

	if direction>=0:
		bl=startCursor.block()
		bl_end=endCursor.block()
	else:
		bl=endCursor.block()
		bl_end=startCursor.block()

	yield bl
	while bl!=bl_end:
		if direction>=0:bl=bl.next()
		# if direction>=0:bl=bl.previous()
		else:bl=bl.previous()
		yield bl
QtGui.QTextCursor.yieldBlockInSelection=yieldBlockInSelection_WW



class RPythonEditor(QtWidgets.QPlainTextEdit):
	def __init__(self,parent=None):
		QtWidgets.QPlainTextEdit.__init__(self,parent=parent)
		self.highlight = syntax.PythonHighlighter(self.document())

		# set monospace font
		font = self.document().defaultFont()
		font.setFamily(FONT['name'])
		font.setPointSize(FONT['size'])
		self.document().setDefaultFont(font)

		# indent :
		fm = QtGui.QFontMetrics(font)
		indent_size = fm.tightBoundingRect(" "*(FONT['indent']+1)).width()-1
		self.setTabStopWidth(indent_size)

		# no wrap
		self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

		self.setup_connections()
	def setup_connections(self):
		# actions
		self.actionCommentDecomment	= QtWidgets.QAction("Comment/Decomment",self)
		self.actionDeleteLine	= QtWidgets.QAction("Delete Line",self)
		self.actionDuplicateLine	= QtWidgets.QAction("Duplicate Line",self)
		self.actionMoveLineUp	= QtWidgets.QAction("Move Line Up",self)
		self.actionMoveLineDown	= QtWidgets.QAction("Move Line Down",self)


		self.addAction(self.actionCommentDecomment)
		self.addAction(self.actionDeleteLine)
		self.addAction(self.actionDuplicateLine)
		self.addAction(self.actionMoveLineUp)
		self.addAction(self.actionMoveLineDown)

		self.actionCommentDecomment.setShortcuts(QtGui.QKeySequence("Ctrl+/"))
		self.actionDeleteLine.setShortcuts(QtGui.QKeySequence("Ctrl+Shift+K"))
		self.actionDuplicateLine.setShortcuts(QtGui.QKeySequence("Ctrl+Shift+D"))
		self.actionMoveLineUp.setShortcuts(QtGui.QKeySequence("Ctrl+Up"))
		self.actionMoveLineDown.setShortcuts(QtGui.QKeySequence("Ctrl+Down"))

		self.actionCommentDecomment	.triggered.connect(self.SLOT_actionCommentDecomment)
		self.actionDeleteLine		.triggered.connect(self.SLOT_actionDeleteLine)
		self.actionDuplicateLine	.triggered.connect(self.SLOT_actionDuplicateLine)
		self.actionMoveLineUp		.triggered.connect(self.SLOT_actionMoveLineUp)
		self.actionMoveLineDown		.triggered.connect(self.SLOT_actionMoveLineDown)

	def keyPressEvent(self,e):
		cur = self.textCursor()
		if cur.hasSelection() and (e.key() == QtCore.Qt.Key_Tab):
			# cur.selectBlocks()
			for bl in cur.yieldBlockInSelection():
				cur1 = QtGui.QTextCursor(bl)
				cur1.insertText('\t')
		elif e.key() == QtCore.Qt.Key_Backtab:
			for bl in cur.yieldBlockInSelection():
				cur1 = QtGui.QTextCursor(bl)
				cur1.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor)
				if str(cur1.selectedText())=='\t':
					cur1.removeSelectedText()
		else:
			QtWidgets.QPlainTextEdit.keyPressEvent(self,e)

	def setPlainText(self,text):
		text = text.replace('    ','\t')# we replace the spaces by tabs
		QtWidgets.QPlainTextEdit.setPlainText(self,text)

	def insertFromMimeData(self,source ):
		"""A re-implementation of insertFromMimeData. We have to check the
		typography of what we have just paste.
		TODO : some summary window of all the corrections.
		"""
		text=str(source.text())
		text = text.replace('    ','\t')
		cursor=self.textCursor()
		cursor.insertText(text)

	def SLOT_actionCommentDecomment(self):
		cur1 = self.textCursor()
		cur1.beginEditBlock()

		for current_block in cur1.yieldBlockInSelection():
			# current_block = cur.block()
			if not len((str(current_block.text())).strip())==0:
				#if it is an empty line: do nothing

				cur = QtGui.QTextCursor( current_block )
				cur.movePosition(QtGui.QTextCursor.StartOfBlock)

				# i = current_block.position()
				# end_pos = current_block.position()+current_block.length()
				charAt = lambda x: str(self.document().characterAt(x))
				while (not cur.atBlockEnd()) and charAt(cur.position()) in [' ','\t']:
					cur.movePosition(QtGui.QTextCursor.NextCharacter)
				c = charAt(cur.position())
				if c != '#':
					cur.insertText('# ')
				else:
					cur.deleteChar()
					while charAt(cur.position())==' ':
						cur.deleteChar()
		cur1.endEditBlock()

	def SLOT_actionDeleteLine(self):
		cur = self.textCursor()
		cur.beginEditBlock()
		cur.selectBlocks()
		# cur.select(QtGui.QTextCursor.BlockUnderCursor)
		self.setTextCursor(cur)
		self.cut()
		cur.endEditBlock()
		# if cur.atEnd():
		# cur.deleteChar()

	def SLOT_actionDuplicateLine(self):
		cur = self.textCursor()
		cur.beginEditBlock()
		cur.selectBlocks()
		# cur.select(QtGui.QTextCursor.BlockUnderCursor)
		text = str(cur.selectedText())
		if text[0]!=u'\u2029':# strange newline
			text = '\n'+text
		cur.movePosition(QtGui.QTextCursor.EndOfBlock)
		cur.insertText(text)
		cur.endEditBlock()
		self.setTextCursor(cur)

	def SLOT_actionMoveLineUp(self):
		cur = self.textCursor()
		cur.beginEditBlock()
		if not cur.block().previous().isValid() :
			return False
		# cur.select(QtGui.QTextCursor.BlockUnderCursor)
		cur.selectBlocks()
		text = cur.selectedText()
		if not cur.selectionStart()==0:
			text = text[1:]
			ss = True
		else: ss=False
		cur.removeSelectedText()

		cur.movePosition(QtGui.QTextCursor.StartOfBlock,QtGui.QTextCursor.MoveAnchor)
		p = cur.position()
		cur.insertText(text)
		if ss:
			cur.insertBlock()
		cur.setPosition(p)
		cur.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor,len(text))
		cur.endEditBlock()
		self.setTextCursor(cur)




		# cur = self.textCursor()
		# if not cur.block().previous().isValid() :
		# 	return False
		# # cur.select(QtGui.QTextCursor.BlockUnderCursor)
		# cur.selectBlocks()
		# text = cur.selectedText()[1:]
		# cur.removeSelectedText()
		# cur.movePosition(QtGui.QTextCursor.PreviousBlock,QtGui.QTextCursor.MoveAnchor)
		# p = cur.position()
		# cur.insertText(text)
		# cur.insertBlock()
		# cur.setPosition(p)
		# # cur.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor,len(text))
		# self.setTextCursor(cur)

	def SLOT_actionMoveLineDown(self):
		cur = self.textCursor()
		cur.beginEditBlock()
		if not cur.block().next().isValid() :
			cur.endEditBlock()
			return False
		# cur.select(QtGui.QTextCursor.BlockUnderCursor)
		cur.selectBlocks()
		text=cur.selectedText()
		cur.removeSelectedText()
		if cur.atStart():
			cur.deleteChar()
		else:
			text = text[1:]
			cur.movePosition(QtGui.QTextCursor.NextBlock,QtGui.QTextCursor.MoveAnchor)
		cur.movePosition(QtGui.QTextCursor.EndOfBlock,QtGui.QTextCursor.MoveAnchor)
		cur.insertBlock()
		p = cur.position()
		cur.insertText(text)
		cur.setPosition(p)
		cur.movePosition(QtGui.QTextCursor.StartOfBlock,QtGui.QTextCursor.MoveAnchor)
		cur.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor,len(text))
		self.setTextCursor(cur)
		cur.endEditBlock()

class RMarkdownEditor(QtWidgets.QTextEdit):
	def __init__(self,parent=None):
		QtWidgets.QPlainTextEdit.__init__(self,parent=parent)
		self.highlight = syntax.MarkdownHighlighter(self)

if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	editor=RMakdownEditor()
	# highlight = syntax.PythonHighlighter(editor.document())

	editor.show()
	sys.exit(app.exec_())
