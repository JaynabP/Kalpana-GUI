import sys
import os
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame, QGridLayout
)
import pandas as pd
from matplotlib.backends.backend_qt5agg import(FigureCanvasQTAgg as FigureCanvas,)
from matplotlib.figure import Figure



class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure()
        super().__init__(self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)

    def update_plot(self, x, y, title, xlabel, ylabel):
        self.axes.clear()
        self.axes.plot(x, y, label=title)
        self.axes.set_xlabel(xlabel, fontsize=10)
        self.axes.set_ylabel(ylabel, fontsize=10)
        self.axes.legend(fontsize=8)
        self.axes.grid(True, alpha=0.7)
        self.fig.tight_layout()
        self.draw()
        


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kalpana GUI")
        self.setGeometry(100, 100, 1200, 800)
        self.time_data = []
        self.altitude = []
        self.pressure = []
        self.voltage = []
        self.gyro_r = []
        self.acc_r = []
        self.gnss_altitude = []
        self.data_index=0
        
        self.data=pd.DataFrame()
        self.ui()
        self.load_data()
        self.ui()
        self.update_graphs()
        
        self.start_timer()
        
    def load_data(self):
        try:
            if os.path.exists("data.csv"):
                self.data = pd.read_csv("data.csv")
                print(f"Loaded data.csv with {len(self.data)} rows.")
            else:
                print("Warning: 'data.csv' not found. Using empty data.")
        except Exception as e:
            print(f"Error loading CSV file: {e}")

    def ui(self):
        palette = QPalette()
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 1,0)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0.0, QColor(0,0,0)) 
        gradient.setColorAt(1.0, QColor(190, 151, 205)) 
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 12))
        self.setCentralWidget(self.tabs)
        self.tabs.setStyleSheet("""
    QTabBar::tab {
        height: 40px;  
        width: 240px;  
        font-size: 14px; 
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 600; 
        color: #004466; 
        background: #E7F6F8; 
        border: 1px solid #99C2CC;  
        border-radius: 6px;  
        padding: 6px;
        margin: 6px; 
        text-align: center;  
    }
    QTabBar::tab:hover {
        background: #CCE7EE; 
        color: #003344;  
        border: 1px solid #007C92; 
    }
    QTabBar::tab:selected {
        background: #007C92; 
        color: white;  
        border: 1px solid #005566; 
    }
    QTabBar {
        alignment: center;  
        margin: 5px;  
    }
""")
        self.tabs_layout()
        self.header_layout()
        self.bottom_layout()
        

        
        
    def tabs_layout(self):
        self.telemetry_tab = QWidget()
        self.graph_tab = QWidget()
        self.location_tab = QWidget()
        self.telecast_tab = QWidget()
        self.tabs.addTab(self.telemetry_tab, "Telemetry Data")
        self.tabs.addTab(self.graph_tab, "Graphs")
        self.tabs.addTab(self.location_tab, "Location and 3D Plotting")
        self.tabs.addTab(self.telecast_tab, "Live Telecast")

        self.init_graph_tab()  
  
    def init_graph_tab(self):
        layout = QVBoxLayout()

        graph_frame = QFrame()
        graph_frame.setStyleSheet("background-color: #E6E6FA; border-radius: 10px; padding: 10px;")
        graph_layout = QGridLayout()
        graph_frame.setLayout(graph_layout)
        layout.addWidget(graph_frame)

        self.graph_tab.setLayout(layout)

        self.graphs = {
            "Altitude": PlotCanvas(self),
            "Pressure": PlotCanvas(self),
            "Voltage": PlotCanvas(self),
            "Gyro_R": PlotCanvas(self),
            "ACC_R": PlotCanvas(self),
            "GNSS Altitude": PlotCanvas(self),
        }

        titles = list(self.graphs.keys())
        for i, title in enumerate(titles):
            title_label = QLabel(f"{title} vs Time")
            title_label.setFont(QFont("Arial", 18, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            graph_layout.addWidget(title_label, i // 3 * 2, i % 3)
            graph_layout.addWidget(self.graphs[title], i // 3 * 2 + 1, i % 3)
         
    def header_layout(self):
        top_section=QFrame()
        top_section.setStyleSheet("background-color: #003153; padding: 10px") 
        top_section.setFixedHeight(140)  
        top_layout = QHBoxLayout(top_section)

        software_state_layout = QVBoxLayout()
        software_state_label = QLabel("SOFTWARE STATE")
        software_state_label.setFont(QFont("Arial", 18, QFont.Bold)) 
        software_state_label.setStyleSheet("color: white; text-align: center;")
        launch_button = QPushButton("LAUNCH PAD")
        launch_button.setFixedSize(150, 40) 
        launch_button.setStyleSheet(""" QPushButton { background-color: white; color: black; border: 2px solid #8b0000; border-radius: 20px; padding: 8px; font-size: 10px; font-family: Arial, sans-serif; letter-spacing: 1px; } QPushButton:hover { background-color: #f5f5f5; } QPushButton:pressed { background-color: #d3d3d3; } """)
        software_state_layout.addWidget(software_state_label, alignment=Qt.AlignCenter)
        software_state_layout.addWidget(launch_button, alignment=Qt.AlignCenter)
        
        team_logo_layout = QVBoxLayout()
        team_label = QLabel("TEAM KALPANA : 2024-CANSAT-ASI-023")
        team_label.setFont(QFont("Arial", 20, QFont.Bold))  
        team_label.setStyleSheet("color: white; text-align: center;")
        logo_label = QLabel()
        pixmap = QPixmap("Team Kalpana Logo.png")  
        pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)  
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        team_logo_layout.addWidget(team_label, alignment=Qt.AlignCenter)
        team_logo_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        
        
        time_layout = QVBoxLayout()
        time_heading = QLabel("TIME")
        time_heading.setFont(QFont("Arial", 16, QFont.Bold)) 
        time_heading.setStyleSheet("color: white; text-align: center;")
        self.time_label = QPushButton("00:00:00")
        self.time_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.time_label.setFixedSize(150, 40)  
        self.time_label.setStyleSheet(""" QPushButton { background-color: white; color: black; border: 2px solid #8b0000; border-radius: 20px; padding: 8px; font-size: 10px; font-family: Arial, sans-serif; letter-spacing: 1px; } QPushButton:hover { background-color: #f5f5f5; } QPushButton:pressed { background-color: #d3d3d3; } """)
        time_layout.addWidget(time_heading, alignment=Qt.AlignCenter)
        time_layout.addWidget(self.time_label, alignment=Qt.AlignCenter)
        
        
        
        packet_layout = QVBoxLayout()
        packet_heading = QLabel("PACKET COUNT")
        packet_heading.setFont(QFont("Arial", 16, QFont.Bold)) 
        packet_heading.setStyleSheet("color: white; text-align: center;")
        self.packet_label = QPushButton("0")
        self.packet_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.packet_label.setFixedSize(150, 40)  
        self.packet_label.setStyleSheet(""" QPushButton { background-color: white; color: black; border: 2px solid #8b0000; border-radius: 20px; padding: 8px; font-size: 10px; font-family: Arial, sans-serif; letter-spacing: 1px; } QPushButton:hover { background-color: #f5f5f5; } QPushButton:pressed { background-color: #d3d3d3; } """)
        packet_layout.addWidget(packet_heading, alignment=Qt.AlignCenter)
        packet_layout.addWidget(self.packet_label, alignment=Qt.AlignCenter)
        
        
        top_layout.addLayout(software_state_layout)
        top_layout.addStretch()
        top_layout.addLayout(team_logo_layout)
        top_layout.addStretch()
        top_layout.addLayout(time_layout)
        top_layout.addLayout(packet_layout)
        
        top_section.setLayout(top_layout)
        
        #Adding to the main layout our header layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(top_section)
        main_layout.addWidget(self.tabs)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        
        
        
    #Bottom section
        
    def bottom_layout(self):
        bottom_section=QFrame()
        bottom_section.setFixedHeight(100)
        bottom_layout=QHBoxLayout()
        
        bottom_layout.setSpacing(20)  
        bottom_layout.setAlignment(Qt.AlignCenter)
        
        button_style = """
            QPushButton {
                background-color: #1A5E63;
                color: white;
                font: bold 12px Arial;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #267377;
            }
        """
        buttons = [
            "BOOT", "Set Time", "Calibrate", "ON / OFF",
            "CX", "SIM Enable", "SIM Activate", "SIM Disable"
        ]

        for text in buttons:
            button = QPushButton(text)
            button.setStyleSheet(button_style)
            button.setFixedSize(120, 40) 
            button.clicked.connect(lambda checked, name=text: self.on_button_click(name))
            bottom_layout.addWidget(button) 
        def on_button_click(self, button_name):
         print(button_name)
        
        bottom_section.setLayout(bottom_layout)

        central_layout = self.centralWidget().layout()
        central_layout.addWidget(bottom_section)
 
    
    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start(1000)

    def update_graphs(self):
        """Update the graphs with data."""
        if not self.data.empty and self.data_index < len(self.data):
            try:
                self.time_data.append(self.data_index)
                self.altitude.append(self.data["ALTITUDE"].iloc[self.data_index])
                self.pressure.append(self.data["PRESSURE"].iloc[self.data_index])
                self.voltage.append(self.data["VOLTAGE"].iloc[self.data_index])
                self.gyro_r.append(self.data["GYRO_R"].iloc[self.data_index])
                self.acc_r.append(self.data["ACC_R"].iloc[self.data_index])
                self.gnss_altitude.append(self.data["GNSS_ALTITUDE"].iloc[self.data_index])

                datasets = {
                    "Altitude": (self.altitude, "Altitude"),
                    "Pressure": (self.pressure, "Pressure"),
                    "Voltage": (self.voltage, "Voltage"),
                    "Gyro_R": (self.gyro_r, "Gyro_R"),
                    "ACC_R": (self.acc_r, "ACC_R"),
                    "GNSS Altitude": (self.gnss_altitude, "GNSS Altitude"),
                }

                for title, (values, ylabel) in datasets.items():
                    self.graphs[title].update_plot(self.time_data, values, title, "Time", ylabel)

                self.data_index += 1

            except KeyError as e:
                print(f"Missing column in data: {e}")
            except Exception as e:
                print(f"Error updating graphs: {e}")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

