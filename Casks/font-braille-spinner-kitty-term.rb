cask "font-braille-spinner-kitty-term" do
  version "1.0.2"
  sha256 "cca902bd1a658ede087b12f136dd3623af4e90d82913e4bbb7504be66036813e"

  url "https://github.com/sidkang/homebrew-fonts/releases/download/braille-spinner-kitty-term-v#{version}/BrailleSpinnerKittyTerm-#{version}.zip"
  name "Braille Spinner Kitty Term"
  desc "Fixed-grid private-use Braille spinner glyphs for Kitty terminals"
  homepage "https://github.com/sidkang/homebrew-fonts/tree/master/fonts/braille-spinner-kitty-term"

  font "BrailleSpinnerKittyTerm-Regular.ttf"
end
