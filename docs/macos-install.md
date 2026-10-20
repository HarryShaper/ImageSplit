# Install ImageSplit on macOS

ImageSplit is currently an unsigned prototype, not a public release.
It bundles Python and installs a Finder Quick Action called Split RAW-JPEG.
No separate Python installation is needed.

## Compatibility

Installer 0.1.3 was reported working on Apple Silicon with macOS 15.7.4,
including a separate standard user account.
Intel support and the minimum supported macOS version remain unverified.
Choose a package built for your Mac's processor.

## Install — your usual Mac account

1. Obtain the package and matching SHA-256 checksum from the maintainer.
2. Verify the checksum before opening the package.
3. Double-click the package in Finder.
4. If macOS blocks it because the developer cannot be verified, open
   System Settings → Privacy & Security. Use Open Anyway only after
   confirming that the blocked item is the package you intended to install.
5. Follow Installer's prompts and provide administrator authorization.

This distribution is unsigned and not notarized by the ImageSplit developer.
Do not disable Gatekeeper or SIP, or remove quarantine attributes.
If macOS reports malware, damage, or an invalid package, stop and investigate.
If organizational policy prevents approval, contact the administrator.

The bundled Python may require its own manual approval through
Privacy & Security. If no supported approval option appears, stop and
report the alert. Approving Python in Downloads does not validate the
installed copy.

## Enable — each account, including the standard test account

1. Sign in to the account that will use ImageSplit.
2. In Finder, right-click a folder → Quick Actions → Customize.
3. Enable Split RAW-JPEG.
4. Select one or more disposable test folders.
5. Choose Quick Actions → Split RAW-JPEG.
6. Confirm that images appear inside raw/ and jpg/.

Activation is per user. Administrator authorization during installation
does not automatically enable the action for other users.

Keep personal diagnostic workflows outside ~/Library/Services when testing
the system-installed action. Preserve those workflows rather than deleting them.

Back up valuable photos before sorting. Logs are written to
~/Library/Logs/image_split.log in the account running the action.
