from style_sheet import css_style1
import json
from YT import YouTube
import requests
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QLineEdit, QLabel, QAbstractItemView, \
							 QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem, QStyle, QStyleOptionProgressBar, QStyledItemDelegate
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

'''
1. Instant search function
2. Pull all uploads at once (without the need to keep loadin videos)
3. Sorting
'''

class TableWidgetItem(QTableWidgetItem):
	def __init__(self, val):
		super().__init__()
		self.setTextAlignment(Qt.AlignRight)
		self.setText(val)

	def __lt__ (self, other):
		try:    	
			return float(self.text().replace(',', '')) < float(other.text().replace(',', ''))
		except:
			return QTableWidgetItem.__lt__(self, other)	

# class ProgressDelegate(QStyledItemDelegate):
#     # paint event
#     def paint(self, painter, option, index):    	
#         progressValue = index.data(Qt.UserRole + 100) # data tracker
#         print('Index{0}-{1}'.format(index.row(), progressValue))
#         progressBar = QStyleOptionProgressBar()
#         progressBar.minimum = 0
#         progressBar.maximum = 100
#         progressBar.rect = option.rect
#         progressBar.rect.setHeight(option.rect.height() - 2)
#         # progressBar.rect.setWidth(option.rect.width() - 1)
#         progressBar.rect.setTop(option.rect.top() - 2)
#         progressBar.progress = 0 if progressValue is None else progressValue # integer
#         progressBar.textVisible = True
#         progressBar.textAlignment = Qt.AlignLeft
#         progressBar.text = '\t {0}%'.format(progressValue)
#         QApplication.style().drawControl(QStyle.CE_ProgressBar, progressBar, painter)


class AppDemo(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Uploaded Videos')
		self.setWindowIcon(QIcon('yt.ico'))
		self.window_width, self.window_height  = 2000, 800 ## this is based on the minimum requirement of the smaller monitor 
		self.resize(self.window_width, self.window_height)
		self.setMinimumSize(600, 400)
		# self.setStyleSheet(css_style1(font_size=40))
		self.setStyleSheet(css_style1(font_size=30, button_width=400))

		self.yt = None
		self.service = None

		layout = QVBoxLayout()
		self.setLayout(layout)

		topLayout = QHBoxLayout()
		layout.addLayout(topLayout)

		buttonPullVideo = QPushButton('&Pull', clicked=self.display_video_info)
		topLayout.addWidget(buttonPullVideo)

		topLayout.addStretch()

		buttonConnect = QPushButton('&Connect', clicked=self.connect)
		topLayout.addWidget(buttonConnect)

		buttonExport = QPushButton('Export to CSV')
		topLayout.addWidget(buttonExport)

		infoLayout = QHBoxLayout()
		layout.addLayout(infoLayout)

		infoLayout.addWidget(QLabel('Enter Channel Id: '))
		# self.channelId = QLineEdit()
		self.channelId = QComboBox()
		self.channelId.setEditable(True)
		# self.channelId.setText('UCvVZ19DRSLIC2-RUOeWx8ug')
		infoLayout.addWidget(self.channelId)


		infoLayout.addWidget(QLabel('Channel Name: '))
		self.channelName = QLineEdit()
		infoLayout.addWidget(self.channelName)


		'''
		constant search filter
		'''
		self.searchFilter = QLineEdit()
		self.searchFilter.textChanged.connect(self.search_video)
		layout.addWidget(self.searchFilter)



		self.infoTable = QTableWidget()
		# self.infoTable.setStyleSheet('background-color: red;')
		self.infoTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.infoTable.setColumnCount(9)
		self.infoTable.setSortingEnabled(True)
		self.infoTable.verticalHeader().setDefaultSectionSize(60)
		self.infoTable.setAlternatingRowColors(True)
		self.infoTable.setHorizontalHeaderLabels(('Video Id', 'Video Title', 'Duration', 'Published', 'View Count', 'Likes', 'Dislikes', 'Comments', 'URL'))
		layout.addWidget(self.infoTable)

		# sepcifying which column to use delegate (progress bar)
		# progressColumnIndex = 9
		# delegate = ProgressDelegate(self.infoTable)
		# self.infoTable.setItemDelegateForColumn(progressColumnIndex, delegate)

		bottomLayout = QHBoxLayout()
		layout.addLayout(bottomLayout)

		self.status = QLabel()
		bottomLayout.addWidget(self.status)

		version = QLabel('Created by Jie Jenn | v1.1')
		bottomLayout.addWidget(version, alignment=Qt.AlignRight)

		self.channelId.addItem('UCvVZ19DRSLIC2-RUOeWx8ug')

	def search_video(self, v):
		txt = str(v).lower()
		for row in range(self.infoTable.model().rowCount()):
			if txt in str(self.infoTable.model().index(row, 1).data()).lower():
				self.infoTable.setRowHidden(row, False)
			else:
				self.infoTable.setRowHidden(row, True)



	def display_video_info(self):
		if self.service is None:
			self.status.setText('Please connect to YouTube service')
			return
		elif not self.channelId.currentText():
			self.status.setText('Channel Id is missing')
			return
		else:
			try:
				self.channelName.setText(self.yt.get_channel_name(self.service, self.channelId.currentText()))
			except:
				self.status.setText('Channel not found')

		self.infoTable.clearContents()

		####################################
		# Workaround when sometimes data now showing after updating the view
		self.infoTable.clearSelection()
		self.infoTable.updateGeometries()
		####################################
		self.infoTable.setRowCount(0)

		self.status.setText('Processing...')

		try:
			videos = self.yt.get_upload_videos(self.service, self.channelId.currentText())
		except KeyError as e:
			self.status.setText('Channel not found')
			self.channelName.clear()
			return 
		except Exception as e:
			self.status.setText(str(e))
			return
		else:			
			if len(videos) == 0:
				self.status.setText('No video available')
				return
		# print(videos)
		self.infoTable.setRowCount(len(videos))

		with open('video list.json', 'w') as f:
			json.dump(videos, f)

		self.infoTable.setSortingEnabled(False)			

		for rowIndex, item in enumerate(videos):
			# rowCount = self.infoTable.rowCount()
			# self.infoTable.insertRow(rowCount)

			video_id = item['id']

			# if video_id == 'LG8SdAbMqDM':
			# 	print(item)


			video_title = item['snippet']['title']
			video_published = item['snippet']['publishedAt'][:10]
			viewCount = '{:,.0f}'.format(int(item['statistics']['viewCount'])) if item['statistics'].get('viewCount') else None
			likeCount = str(item['statistics']['likeCount']) if item['statistics'].get('likeCount') else None
			dislikeCount = str(item['statistics']['dislikeCount']) if item['statistics'].get('dislikeCount') else None
			commentCount = str(item['statistics']['commentCount']) if item['statistics'].get('commentCount') else None

			duration = self.yt.convert_duration(item['contentDetails']['duration'])
			

			self.infoTable.setItem(rowIndex, 0, QTableWidgetItem(video_id))
			self.infoTable.setItem(rowIndex, 1, QTableWidgetItem(video_title))
			self.infoTable.setItem(rowIndex, 2, TableWidgetItem(str(duration)))
			self.infoTable.setItem(rowIndex, 3, TableWidgetItem(video_published))
			self.infoTable.setItem(rowIndex, 4, TableWidgetItem(viewCount))
			self.infoTable.setItem(rowIndex, 5, TableWidgetItem(likeCount))
			self.infoTable.setItem(rowIndex, 6, TableWidgetItem(dislikeCount))
			self.infoTable.setItem(rowIndex, 7, TableWidgetItem(commentCount))

			self.infoTable.setCellWidget(rowIndex, 8, self.inser_hyper_link(video_id))


			# print('Video Id {0}'.format(video_id))
			# print('Like Count V {0}'.format(likeCount))
			# print('DisLike Count V {0}'.format(dislikeCount))

			# try:
			# 	progressPercent = int(int(likeCount) / (int(likeCount) + int(dislikeCount)) * 100)
			# except ZeroDivisionError:
			# 	progressPercent = 0
			# except TypeError:
			# 	progressPercent = 0
			

			# print('{0}-{1}'.format(progressPercent, rowIndex))
			# progressItem = QTableWidgetItem()
			# self.status.setText('Processing row {0}'.format(rowIndex + 1))
			# progressItem.setData(Qt.UserRole + 100, progressPercent)
			# self.infoTable.setItem(rowIndex, 9, progressItem)


			# thumbnail_url = item['snippet']['thumbnails']['medium']['url']
			# self.infoTable.setCellWidget(rowIndex, 10, self.create_thumbnail(thumbnail_url))


		self.infoTable.setSortingEnabled(True)	
		self.status.clear()
		self.autofit_column()


	def create_thumbnail(self, url):
		label = QLabel()
		thumbnail_url = url
		self.image = QPixmap()
		image_data = requests.get(thumbnail_url)
		self.image.loadFromData(image_data.content)
		label.setPixmap(self.image)
		return label

	def inser_hyper_link(self, video_id):
		link = QLabel('<a href=\"https://www.youtube.com/watch?v={0}">{0}</a>'.format(video_id))
		link.setTextFormat(Qt.RichText)
		link.setTextInteractionFlags(Qt.TextBrowserInteraction)
		link.setOpenExternalLinks(True)
		# # link.setStyleSheet('background-color: #FFFFFF')
		return link

	def connect(self):
		try:
			self.yt = YouTube()
			self.service = self.yt.connecting()
			self.status.setText('Connected')
		except Exception as e:
			self.status.setText(str(e))

	def autofit_column(self):
		self.infoTable.setColumnWidth(0, 250)
		self.infoTable.setColumnWidth(1, int(self.width() / self.infoTable.columnCount()) + 600)
		self.infoTable.setColumnWidth(2, 200)
		self.infoTable.setColumnWidth(3, 230)
		self.infoTable.setColumnWidth(4, 230)
		self.infoTable.setColumnWidth(5, 200)
		self.infoTable.setColumnWidth(6, 200)
		self.infoTable.setColumnWidth(7, 250)
		self.infoTable.setColumnWidth(8, 250)
		# self.infoTable.setColumnWidth(9, 450)
		# self.infoTable.setColumnWidth(10, 300)


	# def moveEvent(self, event):
	# 	try:
	# 		screenSize = QApplication.screenAt(event.pos()).size()
	# 		if screenSize.width() > 2000:
	# 			self.setStyleSheet(css_style1(font_size=30, button_width=400))
	# 			# self.setMinimumSize(self.window_width, self.window_height)
	# 		else:
	# 			self.setStyleSheet(css_style1(font_size=25, button_width=350))			
	# 			# self.setMinimumSize(int(self.window_width//3), int(self.window_height//3)) # preventing window flickering
	# 	except:
	# 		pass

if __name__ == '__main__':
	app = QApplication(sys.argv)
	# app.setStyleSheet(css_style1(font_size=30))
	demo = AppDemo()
	demo.show()

	try:
		sys.exit(app.exec_())
	except SystemExit:
		print('Closing Window...')