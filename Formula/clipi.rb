class Clipi < Formula
  desc "Local-only MCP browser service with a Chrome Extension bridge"
  homepage "https://git.882816.xyz/sid/clipi"
  version "0.5.4"

  depends_on arch: :arm64
  depends_on :macos

  on_macos do
    on_arm do
      url "https://git.882816.xyz/sid/clipi/releases/download/v#{version}/clipi-#{version}-darwin-arm64.tar.gz"
      sha256 "02a4a692d0c8ea7cc60248563b4fe29809814e693ae48976c3274fabcbeb7258"

      v = version
      resource "chrome_extension" do
        url "https://git.882816.xyz/sid/clipi/releases/download/v#{v}/clipi-extension-chrome-mv3-#{v}.zip"
        sha256 "9c69b39a84b781a9e83fc2324b3d0e4c44017a3d0e5d258cab3678fabc2df3bb"
      end
    end
  end

  def install
    bin.install "clipi", "clipi-admin", "clipi-server"

    resource("chrome_extension").stage do
      pkgshare.install Dir["*"]
    end
  end

  service do
    run [opt_bin/"clipi-server"]
    keep_alive true
    log_path var/"log/clipi.log"
    error_log_path var/"log/clipi.log"
  end

  def caveats
    <<~EOS
      Load the bundled Chrome Extension manually:

        1. Open chrome://extensions.
        2. Enable Developer mode.
        3. Select "Load unpacked".
        4. Select: #{opt_pkgshare}

      Start the local service:
        brew services start clipi

      Then verify that Chrome has connected:
        clipi system.status --input '{}'

      Homebrew manages this installation. Do not use `clipi-admin install`,
      `upgrade`, or `rollback`; upgrade with `brew upgrade clipi` instead.
    EOS
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/clipi --version")
    assert_match version.to_s, shell_output("#{bin}/clipi-admin --version")
    assert_match version.to_s, shell_output("#{bin}/clipi-server --version")
  end
end
