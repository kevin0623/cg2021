#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math
import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QColorDialog,
    QStyleOptionGraphicsItem,
    QFileDialog,
    QInputDialog)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QImage, QTransform
from PyQt5.QtCore import QRectF, Qt


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """

    def __init__(self, *args):
        super().__init__(*args)
        # self.setMouseTracking(True)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.p_list = None
        self.start_point = None

        self.pen_color = QColor(0, 0, 0)

    def start_draw(self, status, algorithm, item_id):
        self.status = status
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None

    def finish_draw(self):
        self.temp_id = self.main_window.get_id()
        self.temp_item = None

    def start_translate(self):
        if self.selected_id == '':
            self.status = ''
            return
        self.status = 'translate'
        self.temp_item = self.item_dict[self.selected_id]
        self.p_list = self.temp_item.p_list

    def start_rotate(self):
        if self.selected_id == '' or self.item_dict[self.selected_id].item_type == 'ellipse':
            self.status = ''
            return
        self.status = 'rotate'
        self.temp_item = self.item_dict[self.selected_id]
        self.p_list = self.temp_item.p_list

    def start_scale(self):
        if self.selected_id == '':
            self.status = ''
            return
        self.status = 'scale'
        self.temp_item = self.item_dict[self.selected_id]
        self.p_list = self.temp_item.p_list

    def start_clip(self, algorithm):
        if self.selected_id == '' or self.item_dict[self.selected_id].item_type != 'line':
            self.status = ''
            return
        self.status = 'clip'
        self.temp_algorithm = algorithm
        self.temp_item = self.item_dict[self.selected_id]
        self.p_list = self.temp_item.p_list

    def finish_clip(self):

        self.start_point = None
        x_min, y_min = self.temp_item.p_list[0]
        x_max, y_max = self.temp_item.p_list[2]
        self.scene().removeItem(self.temp_item)
        clip_list = alg.clip(self.p_list, x_min, y_min, x_max, y_max, self.temp_algorithm)

        if len(clip_list) == 0:
            self.status = ''
            item = self.item_dict.pop(self.selected_id)
            self.selected_id = ''
            self.scene().removeItem(item)
            row = self.list_widget.currentRow()
            self.list_widget.clearSelection()
            self.list_widget.takeItem(row)
            self.p_list = None
        else:
            self.p_list = self.item_dict[self.selected_id].p_list = clip_list
        self.updateScene([self.sceneRect()])

    def start_select(self):
        self.status = 'select'

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        if selected == '':
            return
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        if self.status != 'select':
            self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.pen_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if self.temp_item is None:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,
                                        self.pen_color)
                self.scene().addItem(self.temp_item)
            else:
                if event.buttons() == Qt.RightButton:
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:
                    self.temp_item.p_list.append([x, y])
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.pen_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve':
            if self.temp_item is None:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.pen_color)
                self.scene().addItem(self.temp_item)
            else:
                if ((self.temp_algorithm == 'B-spline' and len(self.temp_item.p_list) >= 4) or
                    (self.temp_algorithm == 'Bezier' and len(self.temp_item.p_list) >= 2)) and\
                        event.buttons() == Qt.RightButton:
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:
                    self.temp_item.p_list.append([x, y])
        elif self.status == 'translate':
            if self.temp_item is not None:
                rect = self.temp_item.boundingRect()
                x1, y1, x2, y2 = rect.getCoords()
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self.start_point = [x, y]
                else:
                    self.start_point = None
        elif self.status == 'rotate' or self.status == 'scale':
            self.start_point = [x, y]
        elif self.status == 'clip':
            self.start_point = [x, y]
            self.temp_item = MyItem('clip_window', 'polygon', [[x, y], [x, y], [x, y], [x, y]], 'DDA', QColor(255, 0, 0))
            self.scene().addItem(self.temp_item)
        elif self.status == 'select':
            selected = self.scene().itemAt(pos, QTransform())
            for item_id, item in self.item_dict.items():
                if item == selected:
                    if self.selected_id != '':
                        self.item_dict[self.selected_id].selected = False
                        self.item_dict[self.selected_id].update()
                        self.updateScene([self.sceneRect()])
                    self.selected_id = item_id
                    self.item_dict[item_id].selected = True
                    self.item_dict[item_id].update()
                    items = self.list_widget.findItems(item_id, Qt.MatchExactly)
                    if len(items) > 0:
                        self.main_window.list_widget.setCurrentItem(items[0])
                    self.updateScene([self.sceneRect()])

        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' or self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon' or self.status == 'curve':
            if event.buttons() == Qt.LeftButton:
                self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'translate':
            # exit(1)
            if self.start_point is not None:
                dx = x - self.start_point[0]
                dy = y - self.start_point[1]
                self.temp_item.p_list = alg.translate(self.p_list, dx, dy)
        elif self.status == 'rotate':
            if self.start_point is not None:
                dx = x - self.start_point[0]
                dy = y - self.start_point[1]
                r = math.atan2(dy, dx)
                self.temp_item.p_list = alg.rotate(self.p_list, self.start_point[0], self.start_point[1],
                                                   math.degrees(r))
        elif self.status == 'scale':
            if self.start_point is not None:
                dx = x - self.start_point[0]
                dy = y - self.start_point[1]
                self.temp_item.p_list = alg.scale(self.p_list, self.start_point[0], self.start_point[1], dx / 100 + 1)
        elif self.status == 'clip':
            x0, y0 = self.start_point
            self.temp_item.p_list = [(x0, y0), (x0, y), (x, y), (x, y0)]
        else:
            return
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line' or self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'translate':
            self.p_list = self.temp_item.p_list
            self.start_point = None
        elif self.status == 'rotate':
            self.p_list = self.temp_item.p_list
            self.start_point = None
        elif self.status == 'scale':
            self.p_list = self.temp_item.p_list
            self.start_point = None
        elif self.status == 'clip':
            self.finish_clip()
        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color: QColor = None,
                 parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id  # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list  # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.color)
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line' or self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type == 'curve':
            x_list, y_list = zip(*self.p_list)
            x_list, y_list = list(x_list), list(y_list)
            x = min(x_list)
            y = min(y_list)
            w = max(x_list) - x
            h = max(y_list) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        select_act = edit_menu.addAction('选择图元')

        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        exit_act.triggered.connect(qApp.quit)
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        select_act.triggered.connect(self.select_action)
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def set_pen_action(self):
        self.statusBar().showMessage('设置画笔')
        col = QColorDialog.getColor()
        self.canvas_widget.pen_color = col

    def reset_canvas_action(self):

        self.statusBar().showMessage('重置画布')
        w, ok = QInputDialog.getInt(self, '重置画布', 'width', 600, 200, 1000, 10)
        if not ok:
            return
        h, ok = QInputDialog.getInt(self, '重置画布', 'height', 600, 200, 1000, 10)
        if not ok:
            return
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.list_widget.clear()
        self.canvas_widget.item_dict.clear()
        self.item_cnt = 0
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, w, h)
        self.canvas_widget.setScene(self.scene)
        self.canvas_widget.setFixedSize(w, h)
        self.canvas_widget.status = ''
        self.resize(w, h)
        self.statusBar().showMessage('空闲')

    def save_canvas_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.statusBar().showMessage('保存画布')
        filename = QFileDialog.getSaveFileName(self, '保存画布', '.', '位图(*.bmp)')
        image = QImage(int(self.scene.width()), int(self.scene.height()), QImage.Format_ARGB32_Premultiplied)
        image.fill(QColor(255, 255, 255))
        painter = QPainter(image)
        self.scene.render(painter, QRectF(image.rect()), self.scene.sceneRect())
        painter.end()
        if filename[0]:
            image.save(filename[0])

    def line_naive_action(self):
        if self.item_cnt > 0:
            self.item_cnt -= 1
        self.canvas_widget.start_draw('line', 'Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        if self.item_cnt > 0:
            self.item_cnt -= 1
        self.canvas_widget.start_draw('line', 'DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        if self.item_cnt > 0:
            self.item_cnt -= 1
        self.canvas_widget.start_draw('line', 'Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        if self.item_cnt > 0:
            self.item_cnt -= 1
        self.canvas_widget.start_draw('polygon', 'DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        if self.item_cnt > 0:
            self.item_cnt -= 1
        self.canvas_widget.start_draw('polygon', 'Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        if self.item_cnt > 0:
            self.item_cnt -= 1
        self.canvas_widget.start_draw('ellipse', None, self.get_id())
        self.statusBar().showMessage('中点圆算法绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        if self.item_cnt > 0:
            self.item_cnt -= 1
        self.canvas_widget.start_draw('curve', 'Bezier', self.get_id())
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        if self.item_cnt > 0:
            self.item_cnt -= 1
        self.canvas_widget.start_draw('curve', 'B-spline', self.get_id())
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移')

    def rotate_action(self):
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转')

    def scale_action(self):
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('Cohen-Sutherland算法裁剪线段')

    def clip_liang_barsky_action(self):
        self.canvas_widget.start_clip('Liang-Barsky')
        self.statusBar().showMessage('Liang-Barsky算法裁剪线段')

    def select_action(self):
        self.canvas_widget.start_select()
        self.statusBar().showMessage('选择图元')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
