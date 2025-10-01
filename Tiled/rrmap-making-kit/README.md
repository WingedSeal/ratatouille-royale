# Instructions

1. Make sure your current directory is `Tiled/rrmap-making-kit`.
2. Download a tileset for visual reference and name it `tileset.png`.
3. Run `poetry run poe gen_tileset <ROW>x<COL>` when
   `<ROW>` is how many rows the image contain and `<COL>` is how many columns the image contain.
   This'll process the image to correct size and generate `tileset.tsx`.
4. Open Tiled and press `<Ctrl+O>` then select `rrmap-making-kit.tiled-project`.
5. Click on `rrmap.tmx` on Project Window.
6. Press `<Alt+MR>` to resize the map.
7. Edit the layers to create a map and save with `<Ctrl+S>`.
   - Input value by using `number-grid` tileset.
   - Input `tile_id` by using `tileset` tileset.
8. Run `poetry run poe tiled_to_rrmap <MAP_NAME>` to convert it to `.rrmap`

## Layers

### \*\_eN

- `_eN` means `*10^N`
- To input value 123456 to `example` layer (123456 = $12*10^4+34*10^2+56$)
  1. Input `12` into `example_e4` layer
  2. Input `34` into `example_e2` layer
  3. Input `56` into `example` layer

### tile_id

Tile's ID for visual rendering

### height

Tile's height
