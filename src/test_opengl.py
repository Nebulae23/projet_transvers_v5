#!/usr/bin/env python
# src/test_opengl.py - Test OpenGL initialization and rendering

import pygame
import sys
import os

# Try to import OpenGL
try:
    from OpenGL.GL import *
    from OpenGL.GL import shaders
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
    print("OpenGL module imported successfully")
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL module import failed")

def test_opengl_context():
    """Test creating an OpenGL context and basic rendering"""
    pygame.init()
    
    print("Setting OpenGL attributes...")
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    
    print("Creating window with OpenGL context...")
    window_size = (800, 600)
    try:
        screen = pygame.display.set_mode(window_size, pygame.OPENGL | pygame.DOUBLEBUF)
        print("Window created successfully with OpenGL flags")
    except pygame.error as e:
        print(f"Failed to create OpenGL window: {e}")
        return False
    
    # Check OpenGL function availability
    print("\nChecking OpenGL function availability:")
    
    functions_to_check = [
        ("glViewport", "glViewport"),
        ("glClear", "glClear"),
        ("glClearColor", "glClearColor"),
        ("glCreateShader", "glCreateShader"),
        ("glShaderSource", "glShaderSource"),
        ("glCompileShader", "glCompileShader"),
        ("glCreateProgram", "glCreateProgram"),
        ("glAttachShader", "glAttachShader"),
        ("glLinkProgram", "glLinkProgram"),
        ("glUseProgram", "glUseProgram"),
        ("glGenVertexArrays", "glGenVertexArrays"),
        ("glGenBuffers", "glGenBuffers")
    ]
    
    for name, func_name in functions_to_check:
        try:
            func = globals()[func_name]
            available = bool(func)
            print(f"  {name}: {'Available' if available else 'NOT available'}")
        except (KeyError, AttributeError):
            print(f"  {name}: NOT available (not found)")
    
    # Test basic OpenGL operations
    print("\nTesting basic OpenGL operations:")
    try:
        glClearColor(0.2, 0.3, 0.4, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        print("  Basic rendering operations successful")
        
        # Try to get OpenGL version
        try:
            version = glGetString(GL_VERSION)
            if version:
                print(f"  OpenGL Version: {version.decode('utf-8')}")
            else:
                print("  Could not get OpenGL version string")
        except Exception as e:
            print(f"  Error getting OpenGL version: {e}")
            
        # Check if shaders are available
        if bool(glCreateShader):
            print("  Shader support: Available")
            
            # Try to create a simple shader program
            try:
                vertex_shader = """
                #version 330 core
                in vec3 position;
                void main() {
                    gl_Position = vec4(position, 1.0);
                }
                """
                
                fragment_shader = """
                #version 330 core
                out vec4 FragColor;
                void main() {
                    FragColor = vec4(1.0, 1.0, 1.0, 1.0);
                }
                """
                
                # Compile shaders
                vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
                fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
                
                # Create program
                program = shaders.compileProgram(vs, fs)
                print("  Shader compilation: Successful")
            except Exception as e:
                print(f"  Shader compilation failed: {e}")
        else:
            print("  Shader support: NOT available")
        
        pygame.display.flip()
    except Exception as e:
        print(f"  OpenGL operations failed: {e}")
        return False
    
    # Keep window open for a moment
    pygame.time.wait(3000)
    pygame.quit()
    return True

def test_software_fallback():
    """Test software rendering fallback"""
    pygame.init()
    
    print("\nTesting software rendering fallback...")
    screen = pygame.display.set_mode((800, 600))
    
    # Simple drawing operations
    screen.fill((40, 40, 70))
    pygame.draw.rect(screen, (200, 200, 240), (100, 100, 200, 150))
    pygame.draw.circle(screen, (255, 0, 0), (400, 300), 50)
    
    # Add text
    font = pygame.font.SysFont(None, 36)
    text = font.render("Software Fallback Mode", True, (255, 255, 255))
    screen.blit(text, (250, 50))
    
    pygame.display.flip()
    print("Software rendering test complete")
    
    # Keep window open briefly
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    print("=== OpenGL Support Test ===")
    print(f"Pygame version: {pygame.version.ver}")
    
    if OPENGL_AVAILABLE:
        print("OpenGL modules imported successfully.")
        print("\nTesting OpenGL context and rendering:")
        if test_opengl_context():
            print("\nOpenGL test completed successfully!")
        else:
            print("\nOpenGL test failed, trying software fallback")
            test_software_fallback()
    else:
        print("OpenGL modules not available, testing software fallback only")
        test_software_fallback()
    
    print("\nTest completed.") 