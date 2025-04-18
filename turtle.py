import turtle

t = turtle.Turtle()
t.speed(1)

# Add these lines to create a square spiral
colors = ['red', 'purple', 'blue', 'green']
for i in range(100):
    t.pencolor(colors[i % 4])
    t.forward(i * 5)
    t.right(90)

turtle.done()