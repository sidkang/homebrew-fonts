cask "font-braille-spinner-kitty-term" do
  version "1.0.0"
  sha256 "8a6a754552917c834009e62bab862f304439c312273391b658d8a586257ce80a"

  url "https://github.com/sidkang/fonts/releases/download/braille-spinner-kitty-term-v#{version}/BrailleSpinnerKittyTerm-#{version}.zip"
  name "Braille Spinner Kitty Term"
  desc "Fixed-grid private-use Braille spinner glyphs for Kitty terminals"
  homepage "https://github.com/sidkang/homebrew-fonts/tree/master/fonts/braille-spinner-kitty-term"

  font "BrailleSpinnerKittyTerm-Regular.ttf"
end
