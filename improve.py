import pygame
import math

# 初始化 pygame
pygame.init()
WIDTH, HEIGHT = 1000, 700  # 修复：添加逗号
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("鼠标拖拽控制点 + 贝塞尔/B样条切换")
clock = pygame.time.Clock()

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# 控制点（可拖拽）
control_points = [
    [150, 500],
    [300, 200],
    [500, 150],
    [700, 550],
    [850, 300]
]

# 模式：False=贝塞尔，True=B样条
use_bspline = False
dragging = -1  # 当前拖拽的点索引

# ==========================
# 1. 贝塞尔曲线（De Casteljau + 反走样）
# ==========================
def bezier_point(points, t):
    p = [pygame.Vector2(x, y) for x, y in points]
    n = len(p)
    for k in range(1, n):
        for i in range(n - k):
            p[i] = (1 - t) * p[i] + t * p[i+1]
    return (p[0].x, p[0].y)

def draw_antialiased_bezier(screen, points, color, samples=400):
    for i in range(samples + 1):
        t = i / samples
        x, y = bezier_point(points, t)
        # 3x3 邻域反走样渲染
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                cx = x + dx
                cy = y + dy
                # 计算距离与高斯权重
                dist = math.hypot(x - cx, y - cy)
                weight = math.exp(-dist ** 2 / 1.0)
                # 按权重混合颜色
                r = min(255, int(color[0] * weight))
                g = min(255, int(color[1] * weight))
                b = min(255, int(color[2] * weight))
                # 边界检查，避免越界
                if 0 <= int(cx) < WIDTH and 0 <= int(cy) < HEIGHT:
                    screen.set_at((int(cx), int(cy)), (r, g, b))

# ==========================
# 2. 均匀三次B样条曲线
# ==========================
def bspline_point(p0, p1, p2, p3, u):
    u2 = u * u
    u3 = u2 * u
    # 三次B样条基函数系数
    c0 = (-u3 + 3*u2 - 3*u + 1) / 6
    c1 = (3*u3 - 6*u2 + 4) / 6
    c2 = (-3*u3 + 3*u2 + 3*u + 1) / 6
    c3 = u3 / 6
    # 控制点加权求和
    x = p0[0]*c0 + p1[0]*c1 + p2[0]*c2 + p3[0]*c3
    y = p0[1]*c0 + p1[1]*c1 + p2[1]*c2 + p3[1]*c3
    return (x, y)

def draw_uniform_cubic_bspline(screen, ctrl_pts, color, samples=100):
    n = len(ctrl_pts)
    if n < 4:
        return
    # 遍历n-3段曲线
    for i in range(n - 3):
        p0 = ctrl_pts[i]
        p1 = ctrl_pts[i+1]
        p2 = ctrl_pts[i+2]
        p3 = ctrl_pts[i+3]
        # 每段采样100个点
        for j in range(samples + 1):
            u = j / samples
            x, y = bspline_point(p0, p1, p2, p3, u)
            if 0 <= int(x) < WIDTH and 0 <= int(y) < HEIGHT:
                pygame.draw.circle(screen, color, (int(x), int(y)), 1)

# ==========================
# 主循环
# ==========================
running = True
while running:
    screen.fill(WHITE)
    mx, my = pygame.mouse.get_pos()
    mouse_down = pygame.mouse.get_pressed()[0]

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 按B键切换曲线模式
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                use_bspline = not use_bspline

        # 鼠标按下：选中控制点
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, (x, y) in enumerate(control_points):
                if math.hypot(mx - x, my - y) < 15:
                    dragging = i
                    break
        # 鼠标松开：结束拖拽
        if event.type == pygame.MOUSEBUTTONUP:
            dragging = -1

    # 拖拽中：实时更新控制点位置
    if dragging != -1 and mouse_down:
        control_points[dragging] = [mx, my]

    # 绘制控制点
    for i, (x, y) in enumerate(control_points):
        col = GRAY if dragging == i else BLACK
        pygame.draw.circle(screen, col, (int(x), int(y)), 8)

    # 绘制曲线
    if use_bspline:
        draw_uniform_cubic_bspline(screen, control_points, BLUE)
        pygame.display.set_caption("当前：均匀三次B样条 | 鼠标拖拽控制点 | 按B切换")
    else:
        draw_antialiased_bezier(screen, control_points, RED)
        pygame.display.set_caption("当前：反走样贝塞尔 | 鼠标拖拽控制点 | 按B切换")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()