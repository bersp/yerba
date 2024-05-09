---
cover:
  title: Usage example
  subtitle: some example slides to see how [Yerba](color=GREEN) works
  author: Bernado L. Español
---

This is a title
======================================================================
And this is a subtitle
-------------------

Yo can write _text_, _in-line math_ $f(x) = e^{x}$ and math

$$
  [\int](id=1)_0^{x} f'(x)~ [dx](id=1) = f(x) - f(0)
$$

out of line.

>! vspace - 1
>! pause
>! mod - 1, color=RED

Additionally, you can write [colorful things](color=BLUE)

>! pause

```python yerba
a1 = Arrow(start=LEFT+DOWN/3, end=2.5*LEFT+DOWN/3, color=GRAY)
t1 = (p.add_text(r"Also, this space here was added using a `vspace`")
       .next_to(a1, RIGHT))
p.add([a1, t1], box="floating")

p.pause()

a2 = Arrow(start=ORIGIN, end=1.2*UP, color=GRAY).next_to(t1, DOWN)
t2 = p.add_text(r"And this was written directly in Python").next_to(a2, DOWN)

p.add([a2, t2], box="floating")
p.pause()
p.remove([a1, a2, t1, t2])
```

# notitle

You can even do [other things](fill_color=[WHITE,GREEN,WHITE]) with the text and math

$$
  [2](color=RED,id=1) + [3](color=BLUE,id=2)
  = [5](id=3)
$$

>! pause
>! mod - 1, rotate=-90
>! mod - 2, font_size=60
>! bec - 3, p.text("$\pi$")

Grids
======================================================================
A bit about grids and subgrids
---------------------------------

>! def grid - [['A', 'C'], ['B', 'C'], ['D', 'D']], height_ratios=[1, 1, 0.1]

>! set box - 'A', arrange='center'

This is a **box**.
$$
    \int 2 ~d x = 2t
$$

>! set box - 'B'

>! add image - 'example.png', height='100%', draft_mode=True

>! set box - 'C'

Boxes can have different shapes
>! add image - 'example.png', width='100%', draft_mode=False, arrange='center'

>! pause
>! set box - 'D', arrange='center'
>! add - p.named_boxes.content.get_bbox_grid(), box="floating"

These are the defined boxes

Codeblocks
======================================================================
Fragment and Overwrite Codeblocks
---------------------------------
>! set box - 'content', arrange='center'

```markdown fragment - id=1
This text is writen in a `fragment` codeblock.
```
You can change the properties of the fragments on the fly.
>! pause

```markdown fragment - id=2
**You can change their [color](color=RED)**
```
>! mod - 1, color=RED
>! pause

```markdown overwrite - 2
**You can change their _rotation_**
```
>! mod - 1, rotate=180*DEGREES
>! pause

```markdown overwrite - 2
**Or even change the whole text**
```
```markdown overwrite - 1, color=PURPLE
This text was change using an `overwrite` codeblock.
```

Codeblocks
======================================================================
Alternate Codeblocks
---------------------------------
If you are only interested in alternating between different options you can use an `alternate` codeblock:

```markdown alternate - arrange='relative center'
>! add image - 'example.png', height='80%'
---
>! add image - 'example.png', height='80%', draft_mode=True
---
$$
\vec{F} = m\vec{a} [-](font_size=100)
$$
```
