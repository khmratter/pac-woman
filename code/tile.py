class Tile:
    """
    Create a single tile of a map grid.

    Each tile when created has four walls (top, bottom, left, right) and doesn't have a point in it.
    Later, a map grid would consist of such tiles.
    """

    def __init__(self) -> None:
        """
        Construct a tile with all four walls around and no point inside of it.

        Attributes:
        wall_top (bool): define whether the top wall exists (default True)
        wall_bottom (bool): define whether the bottom wall exists (default True)
        wall_left (bool): define whether the left wall exists (default True)
        wall_right (bool): define whether the right wall exists (default True)
        point (bool): define whether the point in the middle of a tile exists (default False)

        Returns: 
        None
        """
        self.wall_top = True
        self.wall_bottom = True
        self.wall_left = True
        self.wall_right = True
        self.point = False
