# Instructions

Install `poetry` using `pip` and run `poetry install`

1. Make sure your current directory is `Tiled/rrmap-making-kit`.
2. Download a tileset for visual reference and name it `tileset.png`.
   2.1 Backup the original tileset image somewhere else.
3. Run `poetry run poe tiled-cli gen_tileset <ROW>x<COL>` when
   `<ROW>` is how many rows the image contain and `<COL>` is how many columns the image contain.
   This'll process the image to correct size and generate `tileset.tsx`.
4. Open Tiled and press `<Ctrl+O>` then select `rrmap-making-kit.tiled-project`.
5. Click on `rrmap.tmx` on Project Window.
6. Press `<Alt+MR>` to resize the map.
7. Edit the layers to create a map and save with `<Ctrl+S>`.
   - Input value by using `number-grid` tileset.
   - Input `tile_id` by using `tileset` tileset.
8. Run `poetry run poe tiled-cli to-rrmap <MAP_NAME>` to convert it to `.rrmap`
   8.1 Backup `rrmap.tmx` somewhere else.
9. Run `poetry run poe tiled-cli reset` to reset the toolkit.

## Layers

### \*\_eN

- `_eN` means `*10^N`
- To input value 123456 to `example` layer (123456 = $12*10^4+34*10^2+56$)
  1. Input `12` into `example_e4` layer
  2. Input `34` into `example_e2` layer
  3. Input `56` into `example` layer

### tile_id

Tile's ID for visual rendering

### \_hex_visual

Serves no purpose but to make hexagone edge easier to look at.
You can either enable or disable the visbility.
Use `hex` tileset to fill it if you change the map size.

### height

Tile's height

### feature_group

Arbitrary numbers for grouping a feature together. Same group number means same feature object.
Only one tile in the group need other metadata. If there is more than 1, others will be ignored.
If there is none, the converter will throw error.

### feature_class

ID for determining feature class. `0` means there is no feature here.

### feature_healh

Feature's health

### feature_defense

Feature's defense

### feature_side

Feature's side

- 0 means `None`
- 1 means `Rat`
- 2 means `Mouse`

Refers to `./src/ratroyale/backend/side.py`

### feature_extra_count

How many unique(extra) parameter(s) this feature class need

### feature_extraN

Unique parameter(s)

Example: If a feature need new parameters called thickness and depth
which is 10 and 23 respectively. `feature_extra_count` will be 2, `feature_extra1` will be `10`
and `feature_extra2` will be `23`

### entity_class

ID for determining entity class. `0` means there's no entity here

### entity_extra_count

Same behavior feature_extra_count

### entity_extraN

Same behavior as feature_extraN
