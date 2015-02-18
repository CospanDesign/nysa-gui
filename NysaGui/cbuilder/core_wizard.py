
from PyQt4.Qt import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from nysa.ibuilder.lib import utils
from nysa.cbuilder import device_manager

INTRO_INFO = "Create a verilog core project"

BUS_SELECTION_INFO = "Wishbone or Axi bus\n"\
                        "\n"\
                        "Wishbone Bus:\n"\
                        "\tSimple\n"\
                        "\tAtomic transactions\n"\
                        "\tSlower Throughput\n"\
                        "\tSmaller Code Foorprint\n"\
                        "\n"\
                        "Axi bus:\n"\
                        "\tMore complicated\n"\
                        "\tSimultaneous transactions\n"\
                        "\tHigher Throughput\n"\
                        "\tLarger Code Footprint"

CORE_CUSTOMIZATION_INFO = "Customize Core"

OUTPUT_DIR_INFO = "Select an directory for the project"

class CoreWizard(QWizard):

    def __init__(self, actions, status):
        super(CoreWizard, self).__init__()
        self.actions = actions
        self.status = status
        self.bus = QComboBox()
        self.bus.addItems(["wishbone", "axi"])
        self.bus.setEnabled(False)
        self.bus.setToolTip("Wishbone is only supported at this time")
        self.bus.setCurrentIndex(0)
        self.core_name = QLineEdit("wb_core1")
        self.core_name.setToolTip("This will name the project as well as the core")
        self.slave_id = 1
        self.slave_sub_id = QLineEdit("0")
        self.slave_sub_id.setValidator(QIntValidator())
        self.slave_sub_id.setToolTip("Add a sub id to help a controlling script distinguish this core from another")
        self.slave_type = "peripheral"
        self.project_path = QLineEdit(utils.get_user_cbuilder_project_dir())
        self.success = None

        self.dma_none = QRadioButton("No DMA")
        self.dma_none.setToolTip("No DMA Functionality")
        self.dma_none.setChecked(True)
        self.dma_reader = QRadioButton("Reader")
        self.dma_reader.setToolTip("DMA Reader Functionality")
        self.dma_writer = QRadioButton("Writer")
        self.dma_writer.setToolTip("DMA Writer Functionality")
        self.dma_box = QHBoxLayout()

        self.dma_box.addWidget(self.dma_none)
        self.dma_box.addWidget(self.dma_reader)
        self.dma_box.addWidget(self.dma_writer)

        self.addPage(self.create_intro_page())
        self.addPage(self.create_bus_selection_page())
        self.addPage(self.create_core_customization_page())
        self.addPage(self.create_output_dir_page())
        self.setWindowTitle("CBuilder Core Creator Wizard")


    def create_intro_page(self):
        self.status.Verbose("Creating intro page")
        page = QWizardPage()
        page.setTitle("Introduction")
        label = QLabel(INTRO_INFO)
        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        page.setLayout(layout)
        return page

    def create_bus_selection_page(self):
        self.status.Verbose("Creating bus selection page")
        page = QWizardPage()
        page.setTitle("Bus Selection")
        label = QLabel(BUS_SELECTION_INFO)
        custom_layout = QFormLayout()

        custom_layout.addRow("Select Bus", self.bus)
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(custom_layout)
        page.setLayout(layout)
        return page

    def get_core_name(self):
        return str(self.core_name.text())

    def get_slave_id(self):
        return self.slave_id

    def get_slave_sub_id(self):
        return self.slave_sub_id

    def get_bus_type(self):
        return str(self.bus.currentText())

    def is_dma_writer(self):
        return self.dma_writer.isChecked()

    def is_dma_reader(self):
        return self.dma_reader.isChecked()

    def get_output_dir(self):
        return str(self.project_path.text())

    def create_core_customization_page(self):
        self.status.Verbose("Creating core customization page")
        page = QWizardPage()
        page.setTitle("Core Customization")

        label = QLabel(CORE_CUSTOMIZATION_INFO)
        self.setup_device_table()

        custom_layout = QFormLayout()
        custom_layout.addRow("Name the core", self.core_name)
        custom_layout.addRow("Device ID", self.t)
        custom_layout.addRow("Slave Sub ID", self.slave_sub_id)
        custom_layout.addRow("DMA reader/writer", self.dma_box)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(custom_layout)

        page.setLayout(layout)
        return page

    def create_output_dir_page(self):
        self.status.Verbose("Creating output dir page")
        page = QWizardPage()
        page.setTitle("Output Directory")

        l = QHBoxLayout()
        select_loc = QPushButton("Select Directory")
        select_loc.clicked.connect(self.output_directory_select)
        l.addWidget(self.project_path)
        l.addWidget(select_loc)

        label = QLabel(OUTPUT_DIR_INFO)
        layout = QVBoxLayout()
        layout.addWidget(label)
        custom_layout = QFormLayout()
        custom_layout.addRow("Project will be created in", l)
        layout.addLayout(custom_layout)
        page.setLayout(layout)
        return page

    def setup_device_table(self):
        #Get the list of devices
        dev_list = device_manager.get_device_list()
        sdev_list = []
        for dev in dev_list:
            if int(dev["ID"], 16) == 0:
                continue
            sdev_list.append(dev)

        dev_list = sdev_list

        self.t = QTableWidget(len(dev_list), 2)
        self.t.setHorizontalHeaderLabels(["ID", "Name"])
        self.t.verticalHeader().setVisible(False)
        self.t.horizontalHeader().setStretchLastSection(True)
        self.t.setSelectionBehavior(QAbstractItemView.SelectRows)
        for dev in dev_list:
            i = dev_list.index(dev)
            self.t.setCellWidget(i, 0, QLabel("%s" % str(dev["ID"])))
            self.t.setCellWidget(i, 1, QLabel(str(dev["name"])))


        self.t.setRangeSelected(QTableWidgetSelectionRange(0, 0, 0, 1), True)
        self.t.itemSelectionChanged.connect(self.core_id_select)


    def core_id_select(self):
        print "select an id"
        r = self.t.currentRow()
        items = self.t.selectedRanges()
        x = items[0].topRow()
        y = items[0].leftColumn()
        #print "%s selected" % items[0].text()
        #print "%s selected" % str(items)
        #print "Coordinates: %d, %d" % (x, y)
        slave_id = str(self.t.cellWidget(x, y).text())
        self.slave_id = int(slave_id, 16)
        self.status.Info("Slave ID Changed to 0x%02X" % self.slave_id)

    def output_directory_select(self):
        path = QFileDialog.getExistingDirectory(None,
                                                caption = "Select a Project Directory",
                                                directory = self.project_path.text())

        if len(path) > 0:
            self.project_path.setText(path)

    def go(self):
        self.show()

