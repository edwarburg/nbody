import argparse
import json
import math
import os
import sys
import random

import jsonpickle
import pygame
from pygame.locals import *

import model

pygame.font.init()

fps = 30

bg_color = pygame.Color(64, 128, 64)
mass_color = pygame.Color(255, 64, 0)
v_arrow_color = pygame.Color(0, 0, 0)
a_arrow_color = pygame.Color(255, 255, 255)

v_draw_factor = 1000
a_draw_factor = 100

next_mass_kg = 1e5
mass_delta = 1e5
next_mass_font = pygame.font.Font(pygame.font.get_default_font(), 32)
next_mass_color = pygame.Color(0, 0, 0)

mass_font = pygame.font.Font(pygame.font.get_default_font(), 10)
mass_font_color = pygame.Color(0, 0, 0)

mass_colors = []

default_fname = "./save.json"

def random_color():
    return pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def draw_mass(m, world, window, mass_color=mass_color):
    windowx, windowy = world_to_window((m.px, m.py), world)
        
    # blob itself
    pygame.draw.circle(window, 
                       mass_color, 
                       world_to_window((m.px, m.py), world), 
                       world_to_window((m.r, 0), world)[0], 
                       0)

def draw_mass_debug_info(m, world, window):
    # velocity vector
    pygame.draw.line(window, 
                     v_arrow_color,
                     world_to_window((m.px, m.py), world), 
                     world_to_window((m.px + (v_draw_factor * m.vx), m.py + (v_draw_factor * m.vy)), world))
    # acceleration vector
    pygame.draw.line(window, 
                     a_arrow_color,
                     world_to_window((m.px, m.py), world), 
                     world_to_window((m.px + (a_draw_factor * m.ax), m.py + (a_draw_factor * m.ay)), world))
    
    m_text = "m={0:.2}".format(m.m)
    v_text = "v=({0:.2}, {1:.2})".format(m.vx, m.vy)
    a_text = "a=({0:.2}, {1:.2})".format(m.ax, m.ay)
    base = world_to_window((m.px + 1, m.py + 1), world)
    window.blit(mass_font.render(m_text, False, mass_font_color), base)
    window.blit(mass_font.render(v_text, False, mass_font_color), (base[0], base[1] + 10))
    window.blit(mass_font.render(a_text, False, mass_font_color), (base[0], base[1] + 20))

def is_visible(m, world, window):
    windowx, windowy = world_to_window((m.px, m.py), world)
    return 0 <= windowx <= pygame.display.get_surface().get_width() and \
           0 <= windowy <= pygame.display.get_surface().get_width()
        
def draw_world(world, window):
    window.fill(bg_color)
    for mass, color in zip(world.masses, mass_colors):
        if is_visible(mass, world, window):
            draw_mass(mass, world, window, color)
    for mass in world.masses:
        if is_visible(mass, world, window):
            draw_mass_debug_info(mass, world, window)

def draw_hud(world, window):
    # next mass kg
    window.blit(next_mass_font.render(str(next_mass_kg) + "kg", False, next_mass_color), (0, pygame.display.get_surface().get_height() - 35))

    # scale
    tl_corner = (5, 5)
    end_point = world_to_window((1e3, 0), world)
    end_point = (end_point[0] + tl_corner[0], end_point[1] + tl_corner[1])

    pygame.draw.line(window,
                     v_arrow_color,
                     tl_corner,
                     end_point)

def window_to_world(pos, world):
    x, y = pos
    worldx = world.maxx * (float(x) / pygame.display.get_surface().get_width())
    worldy = world.maxy * (float(y) / pygame.display.get_surface().get_height())
    return worldx, worldy

def world_to_window(pos, world):
    x, y = pos
    windowx = int(round(pygame.display.get_surface().get_width()  * (float(x) / world.maxx)))
    windowy = int(round(pygame.display.get_surface().get_height() * (float(y) / world.maxy)))
    return windowx, windowy

def random_vec(min, max, length=2, aggregate=tuple):
    return aggregate(random.uniform(min, max) for i in range(length))

def reset_world(world):
    world.clear_masses()
    global mass_colors
    mass_colors = []

def radius_for_mass(m):
    return math.sqrt(float(m) / (2 * mass_delta))

def add_mass(world, mass):
    world.add_mass(mass)
    mass_colors.append(random_color())

def load_from_json(f=default_fname):
    with open(f, "r") as fp:
        world = jsonpickle.decode(fp.read())

    for i in range(len(world.masses)):
        mass_colors.append(random_color())

    return world

def dump_to_json(world, f=default_fname):
    pickled = json.dumps(json.loads(jsonpickle.encode(world)), 
                         indent=4, 
                         sort_keys=True)
    with open(f, "w+") as fp:
        fp.write(pickled)

def handle_keydown(event, world, window, f=default_fname):
    global next_mass_kg, mass_colors
    k = event.key

    if k == K_c:
        world.clear_masses()
    elif k == K_r:
        try:
            new_world = load_from_json(f)

            world.clear_masses()
            mass_colors = []

            for mass in new_world.masses:
                add_mass(world, mass)
        except (IOError, ValueError):
            print >>sys.stderr, "Couldn't reload " + str(f) + "; have you saved anything yet?"
    elif k == K_s:
        dump_to_json(world, f)
    elif k == K_DOWN:
        dm = 10 * mass_delta if pygame.key.get_mods() & KMOD_SHIFT else mass_delta
        next_mass_kg = max(next_mass_kg - dm, mass_delta)
    elif k == K_UP:
        dm = 10 * mass_delta if pygame.key.get_mods() & KMOD_SHIFT else mass_delta
        next_mass_kg += dm
    elif k == K_RIGHT:
        next_mass_kg *= 10
    elif k == K_LEFT:
        next_mass_kg = max(next_mass_kg / 10, mass_delta)
    elif k == K_q:
        pygame.quit()
        sys.exit()

def make_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="?", help="save file to load (json)")
    parser.add_argument("--dt", default=300, type=int, help="time delta to use for simulation. higher is faster. default is 300")
    return parser

def main(*argv):
    parser = make_argparse()
    args = parser.parse_args()

    if args.filename is not None:
        f = args.filename
        world = load_from_json(f)
    else:
        f = default_fname
        world = model.World(5e3, 5e3)

    # time delta for ticks in world sim
    dt = args.dt

    pygame.init()
    pygame.key.set_repeat(250, 10)
    fpsClock = pygame.time.Clock()
    
    maxx, maxy = 1000, 1000
    windowSurfaceObj = pygame.display.set_mode((maxx, maxy))
    pygame.display.set_caption("N-body simulation")

    mousex, mousey = 0, 0
    last_down_x, last_down_y = 0, 0

    try:
        while True:
            draw_world(world, windowSurfaceObj)
            draw_hud(world, windowSurfaceObj)
            if pygame.mouse.get_pressed()[0]:
                pygame.draw.line(windowSurfaceObj,
                                 v_arrow_color,
                                 (last_down_x, last_down_y),
                                 (mousex, mousey))

            world.tick(dt)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    x, y = event.pos

                    add_mass(world, model.Mass(mass=next_mass_kg,
                                               radius=radius_for_mass(next_mass_kg),
                                               position=window_to_world((last_down_x, last_down_y), world),
                                               velocity=window_to_world((float(x - last_down_x) / (v_draw_factor),
                                                                         float(y - last_down_y) / (v_draw_factor)), world),
                                               acceleration=(0, 0)))
                elif event.type == MOUSEBUTTONDOWN:
                    last_down_x, last_down_y = event.pos
                elif event.type == MOUSEMOTION:
                    mousex, mousey = event.pos
                elif event.type == KEYDOWN:
                    handle_keydown(event, world, windowSurfaceObj, f)


            pygame.display.update()
            fpsClock.tick(fps)
    except KeyboardInterrupt:
        print
        return

if __name__ == "__main__":
    main(*sys.argv)

    
