{ pkgs ? import <nixpkgs> {} }:

with pkgs;

mkShell {
  # Sets the build inputs, i.e. what will be available in our
  # local environment.
  buildInputs = [
    python3
    python37Packages.docopt
    python37Packages.pillowfight
    python37Packages.icalendar
    python37Packages.svgwrite
    python37Packages.colour
  ];
}
