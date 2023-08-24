import os

from threading import Thread

from urllib.request import Request, urlopen
from datetime import datetime

# from qt.core import QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QPushButton, QErrorMessage

from qt.core import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QLineEdit, QLayout, QFrame, Qt, QProgressBar, QSpacerItem, QPushButton, QDialogButtonBox, QMetaObject, QCoreApplication

from calibre.utils.config import JSONConfig
from calibre.constants import config_dir
from calibre_plugins.douban_book_metadata.api import get_latest_version
from calibre_plugins.douban_book_metadata.common import is_latest, conversion_size, VersionUpdateThread


prefs = JSONConfig('plugins/douban_book_metadata')

prefs.defaults['douban_bookname_extend_format'] = '{出版年份} - {书名}'


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setupUi()

        self.url = None
        self.commit = self.save_settings
        self._check_version()

    def setupUi(self):
        self.main_layout = QVBoxLayout(self)
        # self.main_layout.setSpacing(2)
        # self.main_layout.setObjectName(u"main_layout")
        # self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.extend_layout = QHBoxLayout()
        self.extend_layout.setSpacing(1)
        self.extend_layout.setObjectName(u"extend_layout")
        self.extend_layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.extend_layout.setContentsMargins(-1, 10, 0, 0)
        self.label = QLabel('在书名中显示出版年份：')
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFrameShape(QFrame.NoFrame)
        self.label.setFrameShadow(QFrame.Plain)
        self.label.setAlignment(Qt.AlignJustify | Qt.AlignTop)
        self.label.setWordWrap(False)
        self.label.setMargin(0)
        self.label.setOpenExternalLinks(False)
        self.label.setTextInteractionFlags(Qt.NoTextInteraction)
        self.extend_layout.addWidget(self.label)

        self.extend_edit = QLineEdit(prefs['douban_bookname_extend_format'])
        # self.extend_edit.setObjectName(u"extend_edit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.extend_edit.sizePolicy().hasHeightForWidth())
        self.extend_edit.setSizePolicy(sizePolicy1)
        self.extend_edit.setFocusPolicy(Qt.StrongFocus)
        self.extend_edit.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.extend_edit.setLayoutDirection(Qt.LeftToRight)
        self.extend_edit.setAutoFillBackground(False)
        self.extend_edit.setToolTip('在书名中显示出版的年份，可以有效的避免同书名、同作者不同版次的书显示不全。显示格式默认是：{出版年份} - {书名}')
        self.extend_layout.addWidget(self.extend_edit)
        self.main_layout.addLayout(self.extend_layout)

        self.info_layout = QVBoxLayout()
        self.info_layout.setObjectName(u"info_layout")
        self.info_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.info_layout.setContentsMargins(-1, 10, -1, 0)
        self.progressBar = QProgressBar(self)
        self.progressBar.setObjectName(u"progressBar")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy2)
        self.progressBar.setValue(79)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setOrientation(Qt.Horizontal)
        # self.progressBar.setTextDirection(QProgressBar.TopToBottom)

        self.info_layout.addWidget(self.progressBar)

        self.info = QLabel(self)
        self.info.setObjectName(u"info")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.info.sizePolicy().hasHeightForWidth())
        self.info.setSizePolicy(sizePolicy3)
        self.info.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.info_layout.addWidget(self.info)
        self.main_layout.addLayout(self.info_layout)

        self.verticalSpacer = QSpacerItem(30, 40, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.main_layout.addItem(self.verticalSpacer)

        self.options_layout = QHBoxLayout()
        # self.options_layout.setObjectName(u"options_layout")
        self.options_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.options_layout.setContentsMargins(-1, 10, -1, 0)
        # self.options_layout.addItem(self.horizontalSpacer)

        self.update_Button = QPushButton('现在更新')
        # self.update_Button.setObjectName(u"pushButton")
        self.options_layout.addWidget(self.update_Button)

        self.install_but = QPushButton('现在安装')
        # self.install_but.setObjectName(u"pushButton_2")
        self.options_layout.addWidget(self.install_but)

        self.main_layout.addLayout(self.options_layout)

        # self.retranslateUi(Form)
        # QMetaObject.connectSlotsByName(Form)
    # setupUi

    # def retranslateUi(self):
    #     self.label_2.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
    #     self.pushButton.setText(QCoreApplication.translate("Dialog", u"PushButton", None))
    #     self.pushButton_2.setText(QCoreApplication.translate("Dialog", u"PushButton", None))
    # retranslateUi

    def _get_version_info(self):
        result = get_latest_version()
        if result is None:
            self.info.setText('当前版本为最新版本。')
        else:
            version = result.get('version')
            latest = is_latest(version)
            self.url = result.get('url')

            if latest == 1:
                size = conversion_size(result.get('size'))
                date_string = datetime.strptime(result.get('updated_date'), '%Y-%m-%dT%H:%M:%SZ')
                date_string = date_string.strftime('%Y年%m月%d日 %H时%M分')
                self.info.setText(
                    f'该插件有最新版本，版本号：{version}，大小：{size}，更新时间：{date_string}')

    def _check_version(self):
        t = VersionUpdateThread(target=self._get_version_info)
        t.start()

        try:
            t.join()
        except Exception as e:
            print('检查版本失败: ' + str(e))
            self.info.setText('检查版本失败: ' + str(e))

    def save_settings(self):
        prefs['douban_bookname_extend_format'] = self.extend_format_edit.text()
        prefs
