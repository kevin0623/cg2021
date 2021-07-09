#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        x, y = x0, y0
        len = abs((x1 - x0) if abs(x1 - x0) > abs(y1 - y0) else (y1 - y0))
        if len == 0:
            result.append((x, y))
        else:
            dx = (x1 - x0) / len
            dy = (y1 - y0) / len
            for i in range(len + 1):
                result.append((round(x), round(y)))
                x = x + dx
                y = y + dy
    elif algorithm == 'Bresenham':
        dx = x1 - x0
        dy = y1 - y0
        xs = 1 if dx > 0 else -1
        ys = 1 if dy > 0 else -1
        dx = abs(dx)
        dy = abs(dy)

        if dx > dy:
            xx, xy, yx, yy = xs, 0, 0, ys  # x增量在x方向的变化
        else:
            dx, dy = dy, dx
            xx, xy, yx, yy = 0, ys, xs, 0  # y增量在y方向的变化

        p = 2 * dy - dx  # bresenham算法决策参数
        y = 0  # 距离起点增量

        for x in range(dx + 1):
            result.append((x0 + x * xx + y * yx, y0 + x * xy + y * yy))
            if p >= 0:
                y += 1
                p -= 2 * dx
            p += 2 * dy

    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []

    xc = int((x0 + x1) / 2)  # 椭圆中心点横坐标
    yc = int((y0 + y1) / 2)  # 椭圆中心点纵坐标
    rx = int(abs(x1 - x0) / 2)
    ry = int(abs(y1 - y0) / 2)

    p = ry ** 2 - rx ** 2 * ry + rx ** 2 / 4  # 决策参数初始值
    x, y = 0, ry
    while ry ** 2 * x < rx ** 2 * y:
        result.append((x, y))
        x = x + 1
        if p < 0:
            p = p + 2 * ry ** 2 * x + ry ** 2
        else:
            y = y - 1
            p = p + 2 * ry ** 2 * x - 2 * rx ** 2 * y + ry ** 2
    p = (ry * (x + 0.5)) ** 2 + rx ** 2 * (y - 1) ** 2 - rx ** 2 * ry ** 2
    while y > 0:
        result.append((x, y))
        y = y - 1
        if p < 0:
            x = x + 1
            p = p + 2 * ry ** 2 * x - 2 * rx ** 2 * y + rx ** 2
        else:
            p = p - 2 * rx ** 2 * y + rx ** 2
    result.append((rx, 0))

    mirror = []
    for x, y in result:
        mirror.append((-x, y))
        mirror.append((x, -y))
        mirror.append((-x, -y))
    tmp = result + mirror
    result = [(x + xc, y + yc) for x, y in tmp]

    return result


def bezier_point(control_points, t):
    if len(control_points) == 1:
        result, = control_points
        return round(result[0]), round(result[1])
    control_linestring = zip(control_points[:-1], control_points[1:])
    return bezier_point([((1 - t) * p1[0] + t * p2[0], (1 - t) * p1[1] + t * p2[1]) for p1, p2 in control_linestring],
                        t)


def deboox_cox(i, k, u):
    if k == 1:
        if i <= u < i+1:
            return 1
        else:
            return 0
    else:
        return (u-i)/(k-1)*deboox_cox(i,k-1,u)+(i+k-u)/(k-1)*deboox_cox(i+1,k-1,u)


def bspline(control_points, t):
    pass
    n = len(control_points) - 1
    m = 3 + n + 1
    # step = 1 / (m - 2 * 3)
    # step = 1 / (n - 2)
    # u = [0, 0, 0]
    # for i in range(n - 1):
    #     u.append(i * step)
    # u = u + [1, 1, 1]
    # k = 3
    u = [i / (n + 4) for i in range(n + 5)]
    k = 3
    # while True:
    #     if u[k] <= t < u[k + 1]:
    #         break
    #     k += 1
    while True:
        if u[k] <= t < u[k + 1] or k == n:
            break
        k += 1
    # t = (t - u[k]) / step
    f0 = (1 - t) ** 3 / 6.0
    f1 = (3 * t ** 3 - 6 * t ** 2 + 4) / 6.0
    f2 = (-3 * t ** 3 + 3 * t ** 2 + 3 * t + 1) / 6.0
    f3 = t ** 3 / 6.0
    p = control_points[k - 3: k + 1]  # 右开区间 ： [k-3, k]
    print(p, k)
    x_ = round(f0 * p[0][0] + f1 * p[1][0] + f2 * p[2][0] + f3 * p[3][0])
    y_ = round(f0 * p[0][1] + f1 * p[1][1] + f2 * p[2][1] + f3 * p[3][1])
    print(x_, y_, t, k)
    return round(f0 * p[0][0] + f1 * p[1][0] + f2 * p[2][0] + f3 * p[3][0]), round(f0 * p[0][1] + f1 * p[1][1] + f2 * p[2][1] + f3 * p[3][1])


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    points_num = 1
    for i in range(len(p_list) - 1):
        points_num += max(abs(p_list[i][0] - p_list[i + 1][0]), abs(p_list[i][1] - p_list[i + 1][1]))
    # points_num = points_num * 2
    if algorithm == 'Bezier':
        if len(p_list) < 2:
            return p_list
        result = [bezier_point(p_list, i / points_num) for i in range(points_num)]
        return result
    elif algorithm == 'B-spline':
        n = len(p_list)
        if n < 4:
            return p_list
        result = []
        # for i in range(points_num):
        #     t = i / points_num
        #     result.append(bspline(p_list, t))
        # return result
        u = 3
        du = (n - 3) / points_num
        while u < n:
            x, y = 0, 0
            for i in range(n):
                k = deboox_cox(i, 4, u)
                x0, y0 = p_list[i]
                x += k * x0
                y += k * y0
            result.append((round(x), round(y)))
            u += du
        return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = [(x + dx, y + dy) for x, y in p_list]
    return result


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    r = math.radians(r)
    result = [(round(x + (u - x) * math.cos(r) - (v - y) * math.sin(r)),
               round(y + (u - x) * math.sin(r) + (v - y) * math.cos(r)))
              for u, v in p_list]
    return result


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = [(round(u * s + x * (1 - s)), round(v * s + y * (1 - s))) for u, v in p_list]
    return result


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min

    if algorithm == 'Cohen-Sutherland':
        INSIDE = 0  # 0000
        LEFT = 1  # 0001
        RIGHT = 2  # 0010
        BOTTOM = 4  # 0100
        TOP = 8  # 1000

        def encode(x_, y_):
            code = INSIDE
            if x_ < x_min:  # to the left of rectangle
                code |= LEFT
            elif x_ > x_max:  # to the right of rectangle
                code |= RIGHT
            if y_ < y_min:  # below the rectangle
                code |= BOTTOM
            elif y_ > y_max:  # above the rectangle
                code |= TOP
            return code

        code0 = encode(x0, y0)
        code1 = encode(x1, y1)

        while True:
            if code0 == 0 and code1 == 0:
                return [(round(x0), round(y0)), (round(x1), round(y1))]
            elif code0 & code1:
                return []

            if code0:
                code_out = code0
            else:
                code_out = code1
            x, y = 0, 0
            if code_out & LEFT:
                x = x_min
                y = y0 + (y1 - y0) / (x1 - x0) * (x_min - x0)
            elif code_out & RIGHT:
                x = x_max
                y = y0 + (y1 - y0) / (x1 - x0) * (x_max - x0)
            elif code_out & TOP:
                x = x0 + (x1 - x0) / (y1 - y0) * (y_max - y0)
                y = y_max
            elif code_out & BOTTOM:
                x = x0 + (x1 - x0) / (y1 - y0) * (y_min - y0)
                y = y_min
            if code_out == code0:
                x0, y0 = x, y
                code0 = encode(x0, y0)
            else:
                x1, y1 = x, y
                code1 = encode(x1, y1)

    elif algorithm == 'Liang-Barsky':
        dx, dy = x1 - x0, y1 - y0
        p1, p2 = -dx, dx
        p3, p4 = -dy, dy
        q1 = x0 - x_min
        q2 = x_max - x0
        q3 = y0 - y_min
        q4 = y_max - y0

        u1, u2 = 0, 1

        if (p1 == 0 and q1 < 0) or (p2 == 0 and q2 < 0) or (p3 == 0 and q3 < 0) or (p4 == 0 and q4 < 0):
            return []
        if p1 != 0:
            r1, r2 = q1 / p1, q2 / p2
            if p1 < 0:
                u1 = max(u1, r1)
                u2 = min(u2, r2)
            else:
                u1 = max(u1, r2)
                u2 = min(u2, r1)
        if p3 != 0:
            r3, r4 = q3 / p3, q4 / p4
            if p3 < 0:
                u1 = max(u1, r3)
                u2 = min(u2, r4)
            else:
                u1 = max(u1, r4)
                u2 = min(u2, r3)

        if u1 > u2:
            return []
        x_0 = round(x0 + u1 * dx)
        y_0 = round(y0 + u1 * dy)
        x_1 = round(x0 + u2 * dx)
        y_1 = round(y0 + u2 * dy)
        return [(x_0, y_0), (x_1, y_1)]
