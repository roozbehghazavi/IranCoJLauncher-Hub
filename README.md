# IranCoJ Launcher

Play **Call of Juarez: Bound in Blood** online with the IranCoJ community: every community map, the
community's mods and a refreshed multiplayer menu. Install one launcher and it keeps all of it up to date.

## Download

| System | Download |
|---|---|
| Windows 10 / 11 | [**IranCoJLauncher-win-x64-Setup.exe**](https://github.com/roozbehghazavi/IranCoJLauncher-Hub/releases/download/launcher/IranCoJLauncher-win-x64-Setup.exe) (or the [portable zip](https://github.com/roozbehghazavi/IranCoJLauncher-Hub/releases/download/launcher/IranCoJLauncher-win-x64-Portable.zip)) |
| Linux | [**IranCoJLauncher-linux-x64.AppImage**](https://github.com/roozbehghazavi/IranCoJLauncher-Hub/releases/download/launcher/IranCoJLauncher-linux-x64.AppImage) |

The launcher updates itself, so you only download it once.

You need your own copy of *Call of Juarez: Bound in Blood* installed (Steam or any other version).

### Linux: first run

The AppImage is the whole launcher in one file, so there is nothing to install. Make it runnable once, then open it:

```bash
chmod +x IranCoJLauncher-linux-x64.AppImage
./IranCoJLauncher-linux-x64.AppImage
```

(Or right-click it → Properties → Permissions → *Allow executing file as program*, then double-click.)

If it doesn't open, or you see an error about `libfuse.so.2`, your system is missing FUSE 2. Install it once:

| Distro | Command |
|---|---|
| Ubuntu 24.04+, Mint 22+ | `sudo apt install libfuse2t64` |
| Ubuntu 22.04, Debian, Mint 21 | `sudo apt install libfuse2` |
| Fedora | `sudo dnf install fuse-libs` |
| Arch, Manjaro, SteamOS (desktop mode) | `sudo pacman -S fuse2` |
| openSUSE | `sudo zypper install libfuse2` |

Can't install it? Run `./IranCoJLauncher-linux-x64.AppImage --appimage-extract-and-run` instead.
On the Steam Deck, open it in Desktop Mode; you can then add it to Steam as a non-Steam game.

## Getting started

1. Install and open the launcher. It finds your game, or you can point it to the game folder.
2. Set up the **IranCoJ Edition**. The launcher builds a separate multiplayer copy from your own game files.
   Your original game is never changed.
3. Press **Play**. Maps and mods download and stay up to date on their own.

## What you get

- **IranCoJ Edition:** a multiplayer-only copy of the game with a new look (menus, in-game screens, HUD and
  fonts), its own menu music, and profiles and settings kept apart from your original game.
- **Every community map**, downloaded and updated automatically.
- **Mods, ready to play.** Server list, spectating, voice chat and the new classes come with the Edition.
  Extra mods can be switched on or off from the launcher at any time.

| Mod | What it does |
|---|---|
| Server List | In-game server list and direct join |
| Spectate | Watch other players from the in-game menu |
| Voice Chat | Talk to other players in game |
| New Classes | Rancher and Redneck as playable classes; Silas Greaves, John Wesley Hardin and Billy the Kid as characters |
| Gore *(optional)* | Richer blood and hit effects |
| No DOF & Motion Blur *(optional)* | A sharper picture without depth of field and motion blur |
| Gun Sounds *(optional)* | Replacement weapon and explosion sounds |

## Credits

- **IranCoJ Launcher and Edition:** Thomas (Roozbeh)
- **Server List Mod:** mx98919
- **Gore Mod, No DOF & Motion Blur:** cr1m3
- **Font:** Oswald, by Vernon Adams and contributors (SIL Open Font License)

*Call of Juarez: Bound in Blood* belongs to its owners. This project ships none of the game's files:
the Edition is built on your computer from the copy you own.
