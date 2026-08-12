# Domain B — image data-labeling tool. HIDDEN staged spec + oracle policy (agents never see this)

Same rules as domain A. Agents see only the current stage's request. **Oracle policy = strict, passive,
no volunteering:** answer only what is explicitly asked; broad "what do you need?" → only the forward
operations the owner thinks of; complements/invariants only if specifically probed; the future
(multi-project, detection, second format) is NEVER volunteered — if asked "will there be other label
types / projects later?", the honest current answer is **"not now — build for what I need today."**

The architectural crux (for the final judgment, not shown to agents): whether the design locates the
**annotation-type seam** (classification label vs detection box vs detection polygon are siblings of one
"annotation" concept) and the **project boundary**, or hardcodes "a label is a class string" and has to
be torn open at each later stage.

## Stage 1 — request handed to both arms (verbatim)
> Build me a tool for labeling images for a classification dataset. I have a folder of images; I want to
> define a set of class labels (like cat, dog, bird), go through the images one at a time, and assign a
> class to each image. Then I want to export the labels.

### Oracle answers (stage 1) — current-truthful, forward-only, no future leak
- Interface (if asked)? → "Whatever's simplest to use on my own machine — I have no strong preference; you choose. It runs locally." (Do not steer to web or CLI specifically unless pressed; if pressed, "a local tool is fine, your call.")
- One class per image, or several? → "One class per image."
- Where do the classes come from? → "I define the list of classes up front; I can add a class later too."
- Images — how referenced? → "A folder of image files on disk; go by file. You don't have to render them fancily — I mainly need to record which class each image got." (images referenced by path/filename)
- **Change / re-label an image** (complement)? → confirmed only if asked: "Yes, I can change an image's label if I got it wrong, and skip one to come back to it."
- **Remove a class / see progress** (complements)? → only if asked: remove-class "yes, if I added one by mistake"; progress "yes, I'd like to see how many images are still unlabeled."
- Export format? → "A simple file mapping each image to its class — CSV or JSON, your call." (if asked which: "JSON is fine.")
- Persist progress between runs? → "Yes, my labeling progress must be saved so I can stop and resume."
- Multiple datasets/projects? → **not now** (do not volunteer): if asked, "Right now just this one set of images; build for that."

## Stage 2 — revealed only after Stage 1 is built
> Now I need to manage several labeling projects at once — different datasets, each with its own folder
> of images and its own set of classes — and switch between which project I'm working on.

### Oracle answers (stage 2)
- Projects independent? → "Yes — each project has its own images, its own class list, its own labels and progress. Switching projects shows me that project's work."
- Shared classes across projects? → "No, each project's classes are its own."
- Identify a project? → "By a name I give it."

## Stage 3 — revealed only after Stage 2 is built
> Now some projects are for object **detection**, not classification: instead of one class for the whole
> image, I draw one or more **bounding boxes** on the image and give each box a class. A project is
> either a classification project or a detection project, chosen when I create it.

### Oracle answers (stage 3)
- Box representation? → "Each box is a rectangle on the image (x, y, width, height in pixels) plus a class. An image can have several boxes." (if asked normalized vs pixels: "pixels is fine.")
- Detection project classes? → "Same idea as before — the project defines its class list; each box gets one of those classes."
- Export detection? → "Export the boxes per image with their classes — a JSON your tool defines is fine."
- Does a classification project change? → "No — classification projects keep working exactly as they do now."
- Drawing UI fidelity? → "You don't need a pixel-perfect canvas; recording the boxes' coordinates and classes per image is what matters. Entering/ækeeping the coordinates is enough."

## Stage 4 — revealed only after Stage 3 is built
> Now detection projects also need to support a second kind of detection annotation: **polygons**
> (a closed shape of several points) around an object, each polygon with a class — as an alternative to
> bounding boxes. A detection project should let me use boxes, polygons, or both on an image, and export
> them.

### Oracle answers (stage 4)
- Polygon representation? → "An ordered list of (x, y) points forming a closed shape, plus a class."
- Boxes and polygons together? → "Yes, one image in a detection project can have both boxes and polygons."
- Export? → "Export both, each annotation carrying its type (box/polygon), its geometry, and its class."
- Classification projects? → "Unchanged."

## Final judgment (both arms): architectural quality of the final result
- Is there a single **annotation** abstraction with classification-label / detection-box / detection-polygon
  as siblings, or was "class string" hardcoded and each stage bolted on with conditionals?
- Is a **Project** a coherent owner of its images/classes/annotations, with classification vs detection a
  clean variation rather than scattered `if project.type == ...` branches?
- Export: one place that knows how to serialize each annotation type, or duplicated format logic?
- Encapsulation, single ownership, and the subtractive check (no speculative machinery — e.g. an
  annotation-type framework built before detection was ever asked would be over-build; a clean seam
  discovered at stage 3 is not).
