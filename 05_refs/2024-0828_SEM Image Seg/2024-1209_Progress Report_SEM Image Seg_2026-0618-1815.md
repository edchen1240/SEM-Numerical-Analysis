2024-1209_Progress Report_SEM Image Seg_2026-0618-1815.md
==============================

# Metadata
- Source PPTX path: D:\01_Floor\a_Ed\08_MIT\06_NMEG\05_Projects\2024-0828_SEM Image Seg\2024-1209_Progress Report_SEM Image Seg.pptx
- Conversion date: 2026-06-18 18:15:01
- Output MD path: D:\01_Floor\a_Ed\08_MIT\06_NMEG\05_Projects\2024-0828_SEM Image Seg\2024-1209_Progress Report_SEM Image Seg_2026-0618-1815.md
- Slide footer: edchen93@mit.edu
- Slide date: 2025-01-29

---

# Content

## [p.1] Machine Learning Examples in 2D Material Development

- Collaboration - 02　　　　Meng-Chi (Ed) Chen　　　　NMEG,

### Side note

- Machine-Learning-Driven Numerical Analysis of SEM Images
- for Optimizing MOCVD-Grown MoS₂ Device Performance

> **Notes:**
>
> The exploration of two-dimensional (2D) materials for next-generation semiconductors begins with recipe optimization to synthesize high-quality 2D materials
> , followed by characterization such as optical microscopy, Raman spectroscopy, atomic force microscopy (AFM), and scanning electron microscopy (SEM).
> Samples with promising quality proceed to device fabrication and performance testing. 
> From experience, we (Jiadi) find that scanning electron microscopy (SEM) images strongly correlate with device outcomes. 
> However, a systematic numerical description of SEM results is lacking. 
> Here, we present an algorithm that leverages machine learning and computer vision to provide a numerical representation (NR) of SEM images of 2D MoS₂, correlating this NR with device performance and using the desired NR for recipe optimization .
> This research is ongoing, with a green checkmark indicating completed functions and a yellow triangle highlighting areas still under development.
> Today, I would like to show you the current stage of this project.

## [p.2] Project Control Table

- .

### Table

| Content | Brief | Type | Link |
| --- | --- | --- | --- |
| TMD CV Analysis | SEM data | Dropbox | https://www.dropbox.com/scl/fo/36wrwwr47m0vifwe8wvnu/AF0F0pOW3Z0kwe34LtRxTuM?rlkey=2v16wbs3bq6vu81e4fph4nnok&st=ibc5brxd&dl=0 |
| MoS2 Material and Performance Characterization | Exp recipe | Google Sheet | https://docs.google.com/spreadsheets/d/1oJ1RdsqrisFb9jxFJyc4TyQTLStmKBVbRIwYu-NxrmI/edit?usp=sharing |
|  |  | .docx |  |
| 2024-0828_SEM Image Seg | Presentation | .pptx | https://mitprod-my.sharepoint.com/:p:/g/personal/edchen93_mit_edu/EeBhIB1nFoVAlkqaQcClEtsBsYqwneUawGiF3oEFSIJpbg?e=pXUIMv |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

## [p.3] Slide 3

![Image: Picture 5](placeholder)

- 3 hr

- 1 hr

- Ignore

- NA.

> **Notes:**
>
> 2024-12-02
> Consider other factors.

## [p.4] How to describe an SEM image of a 2D material?

> **Notes:**
>
> How do we usually describe an SEM image of a 2D material?

## [p.5] How to get these information?

- ImageJ (or other scientific software for microscopic image processing)
  - Require multiple steps of settings and adjustments.
  - Some of our desired function are not exist (or require excessive post process).
- Python
  - Customize the field-specific needs.
  - Streamline the process.

## [p.6] Execution Steps

### Side note

- Pixel per um (sclbar_text, pixel_length_sclbar, pixels_per_um).
- Coverage (pct_black, pct_white).
- Segmentation (cnt_seg_success)
- Nucleation density (nd_per_sqnm)
- Grain size (avg_gs_squm, std_gs_squm)
- Circumference (avg_circumf_um, std_circumf_um)
- Cricumference square to area ratio (avg_csar, std_csar)
- Background noise (avg_bkgd_pixel, std_bkgd_pixel)

- enh_cliplmt=2, enh_tileGrid=8

- Numerical Representation

- Extract scale bar info from SEM image.
- Convent SEM image to grayscale.
- Crop out the center square.
- Enlarge image for better CV processing (cv2.INTER_LINEAR).
- Slightly blur the image (cv2.medianBlur(k=5)).
- Enhance image (CLAHE and merge).
- Binarize image with Otsu's method.
- Calculate coverage and create histogram.
- Watershed image.
- Segment image and save segmentations.
- Calculate segmentation result.
- Save result as excel.

## [p.7] How are these measurements relating to devise performance?

### Side note

- Numerical representation of 2D material SEM images:
- Pixel per um (sclbar_text, pixel_length_sclbar, pixels_per_um).
- Coverage (pct_black, pct_white).
- Segmentation (cnt_seg_success)
- Nucleation density (nd_per_sqnm)
- Grain size (avg_gs_squm, std_gs_squm)
- Circumference (avg_circumf_um, std_circumf_um)
- Cricumference square to area ratio (avg_csar, std_csar)
- Background noise (avg_bkgd_pixel, std_bkgd_pixel)

![Image: Picture 2](placeholder)

### Device

- Performance

![Image: Picture 4](placeholder)

- It might be harder to see the relation of one single measurement relates directly to the device performance.

- ML model can help correlate measurements from SEM image to device performance when there is more data.

## [p.8] Demo Video

### Single folder SEM image segmentation.

- Took 2 mins to process 4 images.

- [OneDrive] Image Seg Demo_480p.mp4

- [Local] Image Seg Demo_1080p.mp4

## [p.9] Slide 9

![Image: Picture 5](placeholder)

![Image: Picture 6](placeholder)

![Image: Picture 10](placeholder)

- Auto Scale Bar Extraction

### Side note

- Average pixel in columns and rows to cut out desired area of scale bar.
- Use pytesseract to read the number of the scale bar.
- The length of scale bar matches the actual pixel checked with Photoshop.

![Image: Picture 25](placeholder)

![Image: Picture 26](placeholder)

## [p.10] Coverage

![Image: Picture 20](placeholder)

### Original

- Gentle Blurred
- Gentle Enhanced
- Binarized

![Image: Picture 15](placeholder)

![Image: Picture 18](placeholder)

![Image: Picture 22](placeholder)

![Image: Picture 23](placeholder)

![Image: Picture 24](placeholder)

![Image: Picture 25](placeholder)

![Image: Picture 26](placeholder)

![Image: Picture 32](placeholder)

- Otsu's method of thresholding: minimizing the intra-class variance.

- Ed: TM92_C-Sapp_02

## [p.11] Otsu’s Method

![Image: Picture 2](placeholder)

### otsu_threshold, arrimg_5bnrz \

- = cv2.threshold(arr_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

## [p.12] Watershed

- Prepare image: grayscale, noise reduction, then binarize.
- Identify background by dilating (extend edge a little bit) the binary image.
- Apply distance transform that turn none-zero pixel into the distance to nearest black pixel.
- Set threshold to make out foreground from the distance transform result.
- Subtract foreground from background to create unknown regions
- Apply watershed by flooding between foreground islands to cut though unknown regions.

- 分水嶺

![Image: Picture 38](placeholder)

![Image: Picture 41](placeholder)

- Prepared image

- Background

![Image: Picture 46](placeholder)

- Distance Transform

![Image: Picture 50](placeholder)

- Foreground

![Image: Picture 54](placeholder)

- Unknown

![Image: Picture 58](placeholder)

- Watershed

- Cut through crystals that sticks together.

![Image: Picture 62](placeholder)

![Image: Picture 63](placeholder)

![Image: Picture 64](placeholder)

![Image: Picture 65](placeholder)

![Image: Picture 66](placeholder)

![Image: Picture 67](placeholder)

## [p.13] Distance Transform

- Distance Transform applied to a binary image so that:
- Black (0) regions remain black, representing the background.
- White (non-zero) regions are transformed so each pixel's value represents the distance (in pixels) to the nearest black (0) pixel.

- 分水嶺

![Image: Picture 25](placeholder)

![Image: Picture 27](placeholder)

- Input image

- After distance transform

![Image: Picture 32](placeholder)

![Image: Picture 34](placeholder)

![Image: Picture 2](placeholder)

## [p.14] Watershed Parameter Adjustments

- frgd_thrs_ratio is a parameter between 0 and 1 that controls the erosion from the edge of foreground.

- 0.3

![Image: Picture 6](placeholder)

![Image: Picture 20](placeholder)

![Image: Picture 22](placeholder)

![Image: Picture 24](placeholder)

![Image: Picture 26](placeholder)

- 0.4

- 0.5

- 0.6

- 0.7

- Linked error

- Missing error

- Too high, some foregrounds are missing.

- Too small, some foregrounds are linked together.

### Side note

- It’s hard to find a middle ground that both error won’t occur.
- Setting suitable for this image might not be suitable for another image.

## [p.15] Watershed Improvement — Add foreground at local maxima

### Side note

- Move a searching window through the image to find local maximum.
- If a maximum is found, mark it with white, so that it will be recognized as a foreground (island) in the later watershed.

## [p.16] Foreground Sharp Edge Smoothing

- Some crystal have sharp edge that during foreground extraction, a single crystal will become multiple crystals, causing error in the later watershed.
- Solution: Applied edge smooth to the extracted foreground, then proceed watershed.

![Image: Picture 15](placeholder)

![Image: Picture 35](placeholder)

- Input

- Foreground/Background overlay

- Normal case.

- This issue case.

- Corrected result.

## [p.17] Slide 17

### Side note

- (a) Image process: Crop, enlarge, blur, enhance, and watershed.
- (b) Before segmenting (last of image process).
- (c) Segmentation result (layer by layer).
- (d) Segmentation result (overlap).
- (e) Precessing terminal

- SegmentationApproach with more reliable traditional segmentation process.

![Image: Picture 26](placeholder)

![Image: Picture 28](placeholder)

![Image: Picture 30](placeholder)

- (e)

- (f)

- (g)

## [p.18] Future Work

- Improve the watershed function to better adapt to SEM images in various condition.
- Obtain device data from Jiadi or Yixuan to correlate the numerical representations of SEM images with device performance.
- Conduct literature research on the feasibility of using machine learning models to embed SEM images into dense array representations.

## [p.19] Calibri Light, 32-36, Bold (H=2.8, W=30, x=1, y=0.5)

*Calibri Light, 20-24 Normal*

- Calibri, 16-24, Normal  (H=13, W=30, x=1, y=3.8)
- Calibri, 16-24, Normal  (H=13, W=30, x=1, y=3.8)

## [p.20] Calibri Light, 32-36, Bold (H=2.8, W=30, x=1, y=0.5)

*Calibri Light, 20-24 Normal*

- Calibri, 16-24, Normal  (H=13, W=30, x=1, y=3.8)
- Calibri, 16-24, Normal  (H=13, W=30, x=1, y=3.8)

## [p.21] Slide 21

- 512x512

- 128x128

- 32x32

- 8x8

## [p.22] Future Work

*Calibri Light, 20-24 Normal*

- Crystal Violet
- Patent
- Mobility data (B620 ~B640)

## [p.23] Future Work

*Calibri Light, 20-24 Normal*

- Crystal Violet
- Patent
- Mobility data (B620 ~B640)
