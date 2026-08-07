class Clipi < Formula
  desc "Local-only MCP browser service with a Chrome Extension bridge"
  homepage "https://git.882816.xyz/sid/clipi"
  version "0.5.1"

  depends_on :macos
  depends_on arch: :arm64

  on_macos do
    on_arm do
      url "https://git.882816.xyz/sid/clipi/releases/download/v#{version}/clipi-#{version}-darwin-arm64.tar.gz"
      sha256 "5c070448b4822684d4bcddd60de1a91fa163c6b37971f55190f217777a7255ca"

      resource "chrome_extension" do
        url "https://git.882816.xyz/sid/clipi/releases/download/v#{version}/clipi-extension-chrome-mv3-#{version}.zip"
        sha256 "09315759bce0447b187ece0246b87357654f7f3e1513848f06af4bee62df028e"
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
