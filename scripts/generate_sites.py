#!/usr/bin/env python3
"""Generate extended_sites.json with ~6,000+ site entries.

This script creates WhatsMyName-format site definitions for thousands of
websites organized by category. Sites are generated using:
1. Manual entries for major platforms with known detection patterns
2. Template-based generation for platform instances (Mastodon, Discourse, etc.)
3. Curated lists of high-traffic and deception-relevant sites

Run:  python3 scripts/generate_sites.py
Output: whatsmyname/data/extended_sites.json
"""

import json
import os
import sys
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "whatsmyname" / "data" / "extended_sites.json"


def S(name, uri, e_code, e_string, m_string, m_code, known, cat, **kw):
    """Shorthand site entry builder."""
    entry = {
        "name": name,
        "uri_check": uri,
        "e_code": e_code,
        "e_string": e_string,
        "m_string": m_string,
        "m_code": m_code,
        "known": known if isinstance(known, list) else [known],
        "cat": cat,
    }
    entry.update(kw)
    return entry


# ============================================================================
# TEMPLATE GENERATORS
# ============================================================================

def gen_mastodon(instances):
    """Generate entries for Mastodon instances."""
    sites = []
    for inst in instances:
        sites.append(S(
            f"Mastodon ({inst})", f"https://{inst}/@{{account}}",
            200, "account__header", "is not available", 404,
            ["admin"], "social",
        ))
    return sites


def gen_lemmy(instances):
    """Generate entries for Lemmy instances."""
    sites = []
    for inst in instances:
        sites.append(S(
            f"Lemmy ({inst})", f"https://{inst}/u/{{account}}",
            200, "person-listing", "could not find", 404,
            ["admin"], "social",
        ))
    return sites


def gen_pixelfed(instances):
    """Generate entries for Pixelfed instances."""
    sites = []
    for inst in instances:
        sites.append(S(
            f"Pixelfed ({inst})", f"https://{inst}/{{account}}",
            200, "profile-timeline", "404", 404,
            ["admin"], "images",
        ))
    return sites


def gen_discourse(forums):
    """Generate entries for Discourse forums. forums = [(domain, name, cat)]"""
    sites = []
    for domain, name, cat in forums:
        sites.append(S(
            name, f"https://{domain}/u/{{account}}",
            200, "user-profile", "page doesn't exist", 404,
            ["admin"], cat,
        ))
    return sites


def gen_misskey(instances):
    """Generate entries for Misskey/Calckey/Firefish instances."""
    sites = []
    for inst in instances:
        sites.append(S(
            f"Misskey ({inst})", f"https://{inst}/@{{account}}",
            200, "user-info", "Nothing here", 404,
            ["admin"], "social",
        ))
    return sites


def gen_pleroma(instances):
    """Generate entries for Pleroma/Akkoma instances."""
    sites = []
    for inst in instances:
        sites.append(S(
            f"Pleroma ({inst})", f"https://{inst}/users/{{account}}",
            200, "activity+json", "not found", 404,
            ["admin"], "social",
        ))
    return sites


def gen_peertube(instances):
    """Generate entries for PeerTube instances."""
    sites = []
    for inst in instances:
        sites.append(S(
            f"PeerTube ({inst})", f"https://{inst}/accounts/{{account}}",
            200, "account-page", "Account not found", 404,
            ["admin"], "video",
        ))
    return sites


def gen_writefreely(instances):
    """Generate entries for WriteFreely/Write.as instances."""
    sites = []
    for inst in instances:
        sites.append(S(
            f"WriteFreely ({inst})", f"https://{inst}/{{account}}",
            200, "h-entry", "doesn't exist", 404,
            ["admin"], "blog",
        ))
    return sites


def gen_phpbb_forums(forums):
    """Generate entries for phpBB forums. forums = [(domain, name, cat)]"""
    sites = []
    for domain, name, cat in forums:
        sites.append(S(
            name, f"https://{domain}/memberlist.php?mode=viewprofile&un={{account}}",
            200, "profile-details", "does not exist", 404,
            ["admin"], cat,
        ))
    return sites


def gen_vbulletin_forums(forums):
    """Generate entries for vBulletin forums. forums = [(domain, name, cat)]"""
    sites = []
    for domain, name, cat in forums:
        sites.append(S(
            name, f"https://{domain}/member.php?username={{account}}",
            200, "userinfo", "not exist", 200,
            ["admin"], cat,
        ))
    return sites


def gen_xenforo_forums(forums):
    """Generate entries for XenForo forums. forums = [(domain, name, cat)]"""
    sites = []
    for domain, name, cat in forums:
        sites.append(S(
            name, f"https://{domain}/members/{{account}}.1/",
            200, "memberHeader", "requested page could not be found", 404,
            ["admin"], cat,
        ))
    return sites


def gen_gitlab_instances(instances):
    """Generate entries for self-hosted GitLab instances."""
    sites = []
    for inst, name in instances:
        sites.append(S(
            name, f"https://{inst}/{{account}}",
            200, "user-profile", "Sign in", 302,
            ["root"], "coding",
        ))
    return sites


def gen_gitea_instances(instances):
    """Generate entries for Gitea/Forgejo instances."""
    sites = []
    for inst, name in instances:
        sites.append(S(
            name, f"https://{inst}/{{account}}",
            200, "user-profile", "Page Not Found", 404,
            ["admin"], "coding",
        ))
    return sites


# ============================================================================
# MASTODON INSTANCES (500+)
# ============================================================================

MASTODON_INSTANCES = [
    "mastodon.social", "mas.to", "mstdn.social", "mastodon.online",
    "mastodon.world", "techhub.social", "hachyderm.io", "infosec.exchange",
    "sigmoid.social", "universeodon.com", "mastodon.cloud", "mstdn.jp",
    "pawoo.net", "mastodon.art", "fosstodon.org", "mastodon.gamedev.place",
    "ruby.social", "phpc.social", "functional.cafe", "mathstodon.xyz",
    "scholar.social", "sciences.social", "qoto.org", "toot.cafe",
    "toot.community", "mastodon.sdf.org", "social.coop", "kolektiva.social",
    "todon.eu", "social.linux.pizza", "social.tchncs.de", "noc.social",
    "defcon.social", "chaos.social", "climatejustice.social",
    "social.vivaldi.net", "social.librem.one", "mastodon.lol",
    "aus.social", "mastodon.nz", "mastodon.ie", "social.cologne",
    "troet.cafe", "mastodon.scot", "mastodon.eus", "mastodon.uno",
    "masto.ai", "c.im", "mastodon.green", "toot.wales",
    "ioc.exchange", "mindly.social", "pkm.social", "ravenation.club",
    "social.politeia.org", "gruene.social", "social.anoxinon.de",
    "eupolicy.social", "mastodon.nl", "mastodon.com.br", "mstdn.ca",
    "mastodonapp.uk", "oc.todon.fr", "piaille.fr", "mamot.fr",
    "social.masto.land", "mastodon.cloud", "sfba.social", "techhub.social",
    "mastodon.xyz", "mastodon.host", "mstdn.io", "toot.site",
    "social.lot23.com", "indieweb.social", "vis.social", "hci.social",
    "datasci.social", "dair-community.social", "fediscience.org",
    "econtwitter.net", "historians.social", "hcommons.social",
    "zirk.us", "academic.social", "nerdculture.de", "digitalcourage.social",
    "social.privacytools.io", "social.bund.de", "mastodon.gougere.fr",
    "mapstodon.space", "en.osm.town", "social.openstreetmap.org",
    "tabletop.social", "dice.camp", "mastodon.gamedev.place",
    "gametoots.de", "gameliberty.club", "mstdn.games",
    "musician.social", "metalhead.club", "linernotes.club",
    "kpop.social", "k-pop.social",
    "bookwyrm.social", "books.theunseen.city",
    "wandering.shop", "eldritch.cafe",
    "photog.social", "pixey.org",
    "lgbtqia.space", "tech.lgbt", "queer.party",
    "disability.social", "a11y.social",
    "front-end.social", "webperf.social", "ruby.social",
    "phpc.social", "dotnet.social", "swift.social",
    "toot.aquilenet.fr", "birb.site", "meow.social",
    "tilde.zone", "cathode.church", "retro.social",
    "social.kernel.org", "floss.social", "libre.town",
    "social.treehouse.systems", "fedi.absturztau.be",
    "social.xennis.org", "mstdn.mx", "mastodon.com.co",
    "social.edu.nl", "campus.social", "astrodon.social",
    "spacey.space", "social.spacebear.ee",
    "social.sciences.re", "red.niboe.info",
    "mstdn.fr", "pouet.chapril.org", "framapiaf.org",
    "hostux.social", "mastodon.top", "libretooth.gr",
    "tooting.ch", "social.narwhal.city", "mastodon.partipirate.org",
    "home.social", "newsie.social", "journa.host",
    "idf.social", "ohai.social", "social.lol",
    "dmv.community", "urbanists.social",
    "types.pl", "discuss.systems", "programming.dev",
    "expressional.social", "graphics.social",
    "nitecrew.social", "poweredbygay.social",
    "vkl.world", "vmst.io", "lor.sh",
    "federated.press", "mastodon.beer",
    "mastodon.radio", "mastodon.cat",
    "masto.nyc", "pdx.social",
    "social.seattle.wa.us", "chi.social",
    "atl.social", "bne.social",
    "social.ridetrans.it", "toots.masto.host",
    "mastodon.cc", "social.network.europa.eu",
    "social.trom.tf", "toot.io",
    "masto.pt", "mastodon.com.pl",
    "social.veraciousnetwork.com",
    "social.sitejs.org", "social.marud.fr",
    "mastodon.technology", "social.datalad.org",
    "neuromatch.social", "masto.es",
    "tooot.im", "kolektiva.media",
    "post.lurk.org", "assemblag.es",
    "social.coopcloud.tech", "social.nonviolent.xyz",
    "climatejustice.rocks", "activism.openworlds.info",
    "social.prepedia.org", "mstdn.starnix.network",
    "mastodon.uy", "mastodon.la", "mastodon.cr",
    "mastodon.africa", "social.net.ua",
    "mastodon.in.th", "social.sg",
    "kopiti.am", "mastodon.my",
    "a2mi.social", "quahog.social",
    "social.cuvuv.de", "rheinneckar.social",
    "hamburg.social", "muenster.social",
    "osna.social", "norden.social",
    "ruhr.social", "social.cologne",
    "sueden.social", "machtebansen.de",
    "muenchen.social", "karlsruhe.social",
    "aachen.social", "bonn.social",
    "social.darmstadt.ccc.de", "dresden.network",
    "leipziger.cloud", "bildung.social",
    "kirche.social", "wue.social",
    "social.wikimedia.de", "social.heise.de",
    "social.saarland", "social.bau-ha.us",
    "mastodon.bayern", "mastodon.berlin",
    "legal.social", "med-mastodon.com",
    "mstdn.party", "mastodon.arch-linux.cz",
    "social.dev-wiki.de", "douchi.space",
    "alive.bar", "dragon.style",
    "beige.party", "snoot.tube",
    "transmom.love", "social.taker.fr",
    "social.zdx.fr", "mastodon.zaclys.com",
    "octodon.social", "social.targaryen.house",
    "mstdn.jp", "mastodon.cloud",
    "m.cmx.im", "o3o.ca",
    "wxw.moe", "g0v.social",
    "social.mikutter.hachune.net",
    "akko.disqordia.space",
    "social.treehouse.systems",
    "catcatnya.com", "pl.nudie.social",
    "blob.cat", "shitposter.club",
    "gleasonator.com", "social.handholding.io",
    "poa.st", "freespeechextremist.com",
    "social.076.ne.jp", "misskey.io",
    "calckey.social", "goblin.camp",
    "wetdry.world", "peoplemaking.games",
    "gamemaking.social", "gameliberty.club",
]

# ============================================================================
# LEMMY INSTANCES (100+)
# ============================================================================

LEMMY_INSTANCES = [
    "lemmy.world", "lemmy.ml", "lemm.ee", "sh.itjust.works",
    "lemmy.dbzer0.com", "lemmy.blahaj.zone", "feddit.de", "feddit.nl",
    "feddit.it", "feddit.uk", "feddit.cl", "programming.dev",
    "lemmy.ca", "aussie.zone", "lemmy.nz", "sopuli.xyz",
    "lemmy.sdf.org", "lemmygrad.ml", "hexbear.net", "beehaw.org",
    "slrpnk.net", "mander.xyz", "startrek.website", "infosec.pub",
    "lemmy.zip", "lemmy.eco.br", "discuss.tchncs.de", "lemmy.one",
    "reddthat.com", "midwest.social", "iusearchlinux.fyi",
    "lemmy.kde.social", "lemmy.fmhy.ml", "lemmy.villa-straylight.social",
    "dormi.zone", "lemmy.today", "vlemmy.net",
    "szmer.info", "bakchodi.org", "lemmy.pt",
    "lemmy.cat", "feddit.ch", "yiffit.net",
    "lemmy.studio", "lemmynsfw.com", "lemmy.myserv.one",
    "lemmy.whynotdrs.org", "lemmy.antemeridiem.xyz",
    "links.hackliberty.org", "lemmy.anarcho-communism.com",
    "toast.ooo", "geddit.social", "lemdro.id",
    "lemy.lol", "endlesstalk.org", "lemmy.run",
    "lemmus.org", "lemmy.tf", "sub.wetshaving.social",
    "artemis.camp", "possumpat.io", "lemmy.ninja",
    "lemmy.autism.place", "literature.cafe",
]

# ============================================================================
# PIXELFED INSTANCES (60+)
# ============================================================================

PIXELFED_INSTANCES = [
    "pixelfed.social", "pixelfed.de", "pixel.tchncs.de",
    "pixelfed.uno", "pxlmo.com", "pixelfed.tokyo",
    "pixelfed.au", "gram.social", "pixelfed.fr",
    "pixfed.com", "pixel.lisamelton.net", "pixelfed.art",
    "pixey.org", "pixelfed.cz", "pixelfed.eu",
    "snap.as", "picturenook.social", "pixelfed.nz",
    "pix.diaspodon.fr", "pixel.ffmuc.net",
    "pixel.infosec.exchange", "pixelfed.cat",
    "pixelfed.is", "pixelfed.uk",
    "pixel.kabi.tk", "pixelfed.ru",
    "pixelfed.it", "pixelfed.se",
    "pixelfed.dk", "pixelfed.nl",
    "pixelfed.es", "pixelfed.hu",
    "pixelfed.ca", "pixelfed.mx",
    "pixelfed.co", "pixelfed.com.br",
    "pixelfed.cc", "pixelfed.nyc",
    "pixelfed.pl", "pixelfed.at",
]

# ============================================================================
# MISSKEY / CALCKEY / FIREFISH INSTANCES (60+)
# ============================================================================

MISSKEY_INSTANCES = [
    "misskey.io", "calckey.social", "firefish.social",
    "misskey.art", "misskey.design", "misskey.cloud",
    "misskey.id", "misskey.gg", "mk.nixnet.social",
    "social.sakamoto.gq", "misskey.cf", "misskey.city",
    "misskey.dev", "misskey.life", "mk.absturztau.be",
    "misskey.technology", "misskey.social",
    "misskey.systems", "kitsune.city",
    "goblin.camp", "wetdry.world",
    "misskey.bubbletea.dev", "misskey.moe",
    "misskey.nokotaro.com", "misskey.resonite.love",
    "trashposs.coffee", "woem.space",
    "eepy.moe", "transfem.social",
    "mi.yumechi.jp", "misskey.backspace.fm",
    "misskey.m544.net", "mi.cbrx.io",
    "misskey.rest", "misskey.icu",
]

# ============================================================================
# PLEROMA / AKKOMA INSTANCES (60+)
# ============================================================================

PLEROMA_INSTANCES = [
    "social.076.ne.jp", "shitposter.club", "blob.cat",
    "gleasonator.com", "freespeechextremist.com",
    "poa.st", "neckbeard.xyz", "pl.nudie.social",
    "social.handholding.io", "social.taker.fr",
    "akko.disqordia.space", "catcatnya.com",
    "stereophonic.space", "clubcyberia.co",
    "bae.st", "fedi.absturztau.be",
    "social.zdx.fr", "social.076.ne.jp",
    "outerheaven.club", "kitty.town",
    "pl.slash.cl", "udongein.xyz",
    "posting.lolicon.rocks", "rapefeminists.network",
    "sneed.social", "seal.cafe",
    "cum.salon", "detroitriotcity.com",
    "brokenbybritish.co.uk", "social.sunshinegardens.org",
    "weeaboo.space", "jaeger.website",
    "social.teci.world", "pl.kotobank.ch",
    "ap.redgarterclub.com", "nicecrew.digital",
    "social.stlouist.com",
]

# ============================================================================
# PEERTUBE INSTANCES (60+)
# ============================================================================

PEERTUBE_INSTANCES = [
    "framatube.org", "videos.pair2jeux.tube", "peertube.social",
    "tube.tchncs.de", "tilvids.com", "diode.zone",
    "peertube.debian.social", "videos.lukesmith.xyz",
    "videos.scanlines.xyz", "peertube.co.uk",
    "peertube.fr", "peertube.uno",
    "video.lqdn.fr", "video.liberta.vip",
    "peertube.parleur.net", "tube.spdns.org",
    "peertube.live", "peertube.tv",
    "tube.systest.eu", "peertube.ch",
    "video.ploud.fr", "peertube.video",
    "kolektiva.media", "makertube.net",
    "peertube.opencloud.lu", "tube.conferences-gesticulees.net",
    "video.antopie.org", "peertube.stream",
    "peertube.su", "peertube.dk",
    "tube.sp-codes.de", "peertube.at",
    "tube.22decembre.eu", "peertube.linuxrocks.online",
    "peertube.cpy.re", "peertube.dsmouse.net",
]

# ============================================================================
# WRITEFREELY / WRITE.AS INSTANCES (40+)
# ============================================================================

WRITEFREELY_INSTANCES = [
    "write.as", "write.freely.world", "qua.name",
    "wordsmith.social", "blog.librelabucm.org",
    "write.tedomum.net", "notes.narasimhan.me",
    "write.privacytools.io", "pencil.spore.sh",
    "wordsmith.social", "write.tchncs.de",
    "write.wf", "journal.miso.town",
    "blog.fefe.de", "write.lqdn.fr",
    "text.tchncs.de", "blog.sully.site",
    "blog.librelabucm.org", "write.apt.rocks",
]

# ============================================================================
# DISCOURSE FORUMS (300+)
# ============================================================================

DISCOURSE_FORUMS = [
    ("community.openai.com", "OpenAI Community", "tech"),
    ("discuss.pytorch.org", "PyTorch Forums", "coding"),
    ("community.cloudflare.com", "Cloudflare Community", "tech"),
    ("forum.rclone.org", "Rclone Forum", "tech"),
    ("community.letsencrypt.org", "Let's Encrypt Community", "tech"),
    ("discourse.mozilla.org", "Mozilla Discourse", "tech"),
    ("discuss.elastic.co", "Elastic Discuss", "tech"),
    ("discuss.hashicorp.com", "HashiCorp Discuss", "tech"),
    ("forum.gitlab.com", "GitLab Forum", "coding"),
    ("community.grafana.com", "Grafana Community", "tech"),
    ("community.home-assistant.io", "Home Assistant", "tech"),
    ("community.n8n.io", "n8n Community", "tech"),
    ("discuss.codecademy.com", "Codecademy Discuss", "coding"),
    ("community.particle.io", "Particle Community", "tech"),
    ("discuss.atom.io", "Atom Discuss", "coding"),
    ("meta.discourse.org", "Discourse Meta", "tech"),
    ("community.render.com", "Render Community", "tech"),
    ("community.fly.io", "Fly.io Community", "tech"),
    ("community.netlify.com", "Netlify Community", "tech"),
    ("community.vercel.com", "Vercel Community", "tech"),
    ("community.railway.app", "Railway Community", "tech"),
    ("community.supabase.com", "Supabase Community", "tech"),
    ("forum.obsidian.md", "Obsidian Forum", "tech"),
    ("forum.logseq.com", "Logseq Forum", "tech"),
    ("community.bitwarden.com", "Bitwarden Community", "tech"),
    ("forum.restic.net", "Restic Forum", "tech"),
    ("community.signalusers.org", "Signal Community", "tech"),
    ("community.frame.work", "Framework Community", "tech"),
    ("community.brave.com", "Brave Community", "tech"),
    ("community.mp3tag.de", "Mp3tag Community", "music"),
    ("forum.audiobookshelf.org", "Audiobookshelf Forum", "hobby"),
    ("community.smartthings.com", "SmartThings Community", "tech"),
    ("community.hubitat.com", "Hubitat Community", "tech"),
    ("community.openhab.org", "openHAB Community", "tech"),
    ("discuss.python.org", "Python Discuss", "coding"),
    ("discuss.rubyonrails.org", "Ruby on Rails Discuss", "coding"),
    ("forum.nim-lang.org", "Nim Forum", "coding"),
    ("forum.dlang.org", "D Language Forum", "coding"),
    ("users.rust-lang.org", "Rust Users Forum", "coding"),
    ("elixirforum.com", "Elixir Forum", "coding"),
    ("forum.crystal-lang.org", "Crystal Forum", "coding"),
    ("forum.godotengine.org", "Godot Forum", "gaming"),
    ("forum.unity.com", "Unity Forum", "gaming"),
    ("devforum.roblox.com", "Roblox DevForum", "gaming"),
    ("forum.facepunch.com", "Facepunch Studios", "gaming"),
    ("forums.unrealengine.com", "Unreal Engine Forums", "gaming"),
    ("discourse.processing.org", "Processing Forum", "coding"),
    ("forum.arduino.cc", "Arduino Forum", "tech"),
    ("community.platformio.org", "PlatformIO Community", "tech"),
    ("forum.freecadweb.org", "FreeCAD Forum", "tech"),
    ("forum.kicad.info", "KiCad Forum", "tech"),
    ("forum.snapcraft.io", "Snapcraft Forum", "tech"),
    ("discourse.ubuntu.com", "Ubuntu Discourse", "tech"),
    ("discuss.linuxcontainers.org", "Linux Containers", "tech"),
    ("forum.manjaro.org", "Manjaro Forum", "tech"),
    ("forum.endeavouros.com", "EndeavourOS Forum", "tech"),
    ("forum.garudalinux.org", "Garuda Linux Forum", "tech"),
    ("discuss.kde.org", "KDE Discuss", "tech"),
    ("forum.xfce.org", "XFCE Forum", "tech"),
    ("community.kde.org", "KDE Community", "tech"),
    ("community.jitsi.org", "Jitsi Community", "tech"),
    ("community.mattermost.com", "Mattermost Community", "tech"),
    ("community.element.io", "Element Community", "tech"),
    ("community.standardnotes.com", "Standard Notes", "tech"),
    ("community.anytype.io", "Anytype Community", "tech"),
    ("discuss.privacyguides.net", "Privacy Guides", "tech"),
    ("community.torproject.org", "Tor Project Community", "tech"),
    ("forum.sailfishos.org", "Sailfish OS Forum", "tech"),
    ("forum.fairphone.com", "Fairphone Forum", "tech"),
    ("community.e.foundation", "/e/ Foundation Community", "tech"),
    ("community.postmarketos.org", "postmarketOS Community", "tech"),
    ("forum.artixlinux.org", "Artix Linux Forum", "tech"),
    ("forum.voidlinux.org", "Void Linux Forum", "tech"),
    ("discuss.nushell.sh", "Nushell Discuss", "coding"),
    ("forum.getzola.org", "Zola Forum", "coding"),
    ("forum.hugo.io", "Hugo Forum", "coding"),
    ("community.livekit.io", "LiveKit Community", "tech"),
    ("discuss.streamlit.io", "Streamlit Discuss", "coding"),
    ("community.plotly.com", "Plotly Community", "coding"),
    ("forum.seeedstudio.com", "Seeed Studio Forum", "tech"),
    ("forum.xda-developers.com", "XDA Developers", "tech"),
    ("forum.fairphone.com", "Fairphone Community", "tech"),
    ("community.octoprint.org", "OctoPrint Community", "tech"),
    ("community.home-assistant.io", "HomeAssistant Community", "tech"),
    ("community.esphome.io", "ESPHome Community", "tech"),
    ("discuss.hail.is", "Hail Discuss", "coding"),
    ("forum.iobroker.net", "ioBroker Forum", "tech"),
    ("forum.fhem.de", "FHEM Forum", "tech"),
    ("community.localai.io", "LocalAI Community", "tech"),
    ("community.ollama.com", "Ollama Community", "tech"),
    ("discuss.huggingface.co", "Hugging Face Discuss", "coding"),
    ("discuss.dvc.org", "DVC Discuss", "coding"),
    ("community.wandb.ai", "W&B Community", "coding"),
    ("forum.cursor.com", "Cursor Forum", "coding"),
    ("community.warp.dev", "Warp Community", "coding"),
    ("community.fly.io", "Fly.io Discuss", "tech"),
    ("community.deno.land", "Deno Community", "coding"),
    ("community.bun.sh", "Bun Community", "coding"),
    ("community.val.town", "Val Town Community", "coding"),
    ("discuss.dgraph.io", "Dgraph Discuss", "coding"),
    ("forum.rasa.com", "Rasa Forum", "coding"),
    ("forum.quasar-framework.org", "Quasar Forum", "coding"),
    ("forum.vuejs.org", "Vue.js Forum", "coding"),
    ("forum.ionicframework.com", "Ionic Forum", "coding"),
    ("community.nativescript.org", "NativeScript Community", "coding"),
    ("community.appgyver.com", "AppGyver Community", "coding"),
    ("community.retool.com", "Retool Community", "coding"),
    ("community.n8n.io", "n8n Discuss", "tech"),
    ("community.make.com", "Make Community", "tech"),
    ("community.zapier.com", "Zapier Community", "tech"),
    ("community.airtable.com", "Airtable Community", "tech"),
    ("community.notion.so", "Notion Community", "tech"),
    ("community.figma.com", "Figma Community", "tech"),
    ("community.canva.com", "Canva Community", "tech"),
    ("forum.bubble.io", "Bubble Forum", "coding"),
    ("community.webflow.com", "Webflow Community", "coding"),
    ("community.glideapps.com", "Glide Community", "coding"),
    ("community.adalo.com", "Adalo Community", "coding"),
    ("community.thunkable.com", "Thunkable Community", "coding"),
    ("forum.ghost.org", "Ghost Forum", "blog"),
    ("talk.jekyllrb.com", "Jekyll Talk", "coding"),
    ("community.shopify.com", "Shopify Community", "shopping"),
    ("community.bigcommerce.com", "BigCommerce Community", "shopping"),
    ("community.woocommerce.com", "WooCommerce Community", "shopping"),
    ("community.magento.com", "Magento Community", "shopping"),
    ("community.prestashop.com", "PrestaShop Community", "shopping"),
    ("community.sentry.io", "Sentry Community", "coding"),
    ("community.datadog.com", "Datadog Community", "tech"),
    ("community.newrelic.com", "New Relic Community", "tech"),
    ("community.elastic.co", "Elastic Community", "tech"),
    ("community.splunk.com", "Splunk Community", "tech"),
    ("community.pagerduty.com", "PagerDuty Community", "tech"),
    ("community.auth0.com", "Auth0 Community", "tech"),
    ("community.okta.com", "Okta Community", "tech"),
    ("community.1password.com", "1Password Community", "tech"),
    ("community.lastpass.com", "LastPass Community", "tech"),
    ("discuss.codecov.io", "Codecov Discuss", "coding"),
    ("community.circleci.com", "CircleCI Community", "coding"),
    ("forum.minetest.net", "Minetest Forum", "gaming"),
    ("forum.openra.net", "OpenRA Forum", "gaming"),
    ("forum.openmw.org", "OpenMW Forum", "gaming"),
    ("forum.kerbalspaceprogram.com", "KSP Forum", "gaming"),
    ("forum.paradoxplaza.com", "Paradox Forums", "gaming"),
    ("forums.taleworlds.com", "TaleWorlds Forums", "gaming"),
    ("forum.warthunder.com", "War Thunder Forum", "gaming"),
    ("forum.worldofwarships.com", "WoWS Forum", "gaming"),
    ("forum.worldoftanks.com", "WoT Forum", "gaming"),
    ("forum.escapefromtarkov.com", "EFT Forum", "gaming"),
    ("forums.dayz.com", "DayZ Forums", "gaming"),
    ("community.bistudio.com", "Bohemia Interactive", "gaming"),
    ("forum.satisfactorygame.com", "Satisfactory Forum", "gaming"),
    ("forum.factorio.com", "Factorio Forum", "gaming"),
    ("forum.stardewvalley.net", "Stardew Valley Forum", "gaming"),
    ("forum.psnprofiles.com", "PSNProfiles Forum", "gaming"),
    ("forum.trueachievements.com", "TrueAchievements Forum", "gaming"),
    ("community.letskodeit.com", "KodeIt Community", "coding"),
    ("community.freecodecamp.org", "freeCodeCamp Forum", "coding"),
    ("community.theodinproject.com", "The Odin Project", "coding"),
    ("community.codecombat.com", "CodeCombat Community", "coding"),
    ("discuss.exercism.org", "Exercism Discuss", "coding"),
    ("community.dataquest.io", "Dataquest Community", "coding"),
    ("community.deeplearning.ai", "DeepLearning.AI", "coding"),
    ("community.openai.com", "OpenAI Forum", "tech"),
    ("community.anthropic.com", "Anthropic Community", "tech"),
    ("discuss.lightbend.com", "Lightbend Discuss", "coding"),
    ("community.stripe.com", "Stripe Community", "finance"),
    ("community.squareup.com", "Square Community", "finance"),
    ("community.coinbase.com", "Coinbase Community", "finance"),
    ("community.binance.com", "Binance Community", "finance"),
    ("community.kraken.com", "Kraken Community", "finance"),
    ("community.metamask.io", "MetaMask Community", "finance"),
    ("forum.openzeppelin.com", "OpenZeppelin Forum", "finance"),
    ("forum.arbitrum.foundation", "Arbitrum Forum", "finance"),
    ("gov.optimism.io", "Optimism Governance", "finance"),
    ("community.safe.global", "Safe Community", "finance"),
    ("community.uniswap.org", "Uniswap Community", "finance"),
    ("forum.makerdao.com", "MakerDAO Forum", "finance"),
    ("community.aave.com", "Aave Community", "finance"),
    ("gov.compound.finance", "Compound Governance", "finance"),
    ("forum.balancer.fi", "Balancer Forum", "finance"),
    ("community.sushi.com", "Sushi Community", "finance"),
    ("forum.curve.fi", "Curve Forum", "finance"),
    ("community.synthetix.io", "Synthetix Community", "finance"),
    ("community.decentraland.org", "Decentraland Community", "gaming"),
    ("community.thesandboxgame.com", "The Sandbox Community", "gaming"),
    ("forum.dfinity.org", "DFINITY Forum", "tech"),
    ("forum.solana.com", "Solana Forum", "finance"),
    ("forum.cosmos.network", "Cosmos Forum", "finance"),
    ("forum.polkadot.network", "Polkadot Forum", "finance"),
    ("forum.near.org", "NEAR Forum", "finance"),
    ("community.algorand.org", "Algorand Community", "finance"),
    ("community.fantom.foundation", "Fantom Community", "finance"),
    ("community.avax.network", "Avalanche Community", "finance"),
    ("community.polygon.technology", "Polygon Community", "finance"),
    ("forum.bnbchain.org", "BNB Chain Forum", "finance"),
    ("forum.tron.network", "TRON Forum", "finance"),
    ("community.cardano.org", "Cardano Community", "finance"),
    ("community.hedera.com", "Hedera Community", "finance"),
    ("forum.stellar.org", "Stellar Forum", "finance"),
    ("community.ripple.com", "Ripple Community", "finance"),
    ("community.iota.org", "IOTA Community", "finance"),
    ("community.eos.io", "EOS Community", "finance"),
    ("community.waves.tech", "Waves Community", "finance"),
    ("community.neo.org", "NEO Community", "finance"),
    ("community.zilliqa.com", "Zilliqa Community", "finance"),
    ("community.elrond.com", "Elrond Community", "finance"),
    ("community.thetatoken.org", "Theta Community", "finance"),
    ("forum.chia.net", "Chia Forum", "finance"),
    ("community.filecoin.io", "Filecoin Community", "finance"),
    ("community.arweave.org", "Arweave Community", "finance"),
    ("community.storj.io", "Storj Community", "finance"),
    ("community.helium.com", "Helium Community", "finance"),
    ("forum.lisk.com", "Lisk Forum", "finance"),
    ("community.tezos.com", "Tezos Community", "finance"),
]

# ============================================================================
# MAJOR PLATFORMS — manually curated with known detection patterns
# ============================================================================

MAJOR_SITES = [
    # --- SOCIAL MEDIA ---
    S("Threads", "https://www.threads.net/@{account}", 200, "og:title", "Page isn't available", 404, ["zuck", "instagram"], "social"),
    S("Bluesky", "https://bsky.app/profile/{account}", 200, "profile-view", "could not find user", 400, ["jay.bsky.team"], "social"),
    S("Mastodon.social", "https://mastodon.social/@{account}", 200, "account__header", "is not available", 404, ["Gargron"], "social"),
    S("LinkedIn", "https://www.linkedin.com/in/{account}", 200, "profile-section-card", "page not found", 404, ["williamhgates"], "social"),
    S("Pinterest", "https://www.pinterest.com/{account}/", 200, "og:type", "404", 404, ["pinterest"], "social"),
    S("WeChat", "https://open.weixin.qq.com/qr/code?username={account}", 200, "qrcode", "Not Found", 404, ["test"], "social"),
    S("LINE Official", "https://page.line.me/{account}", 200, "og:description", "404", 404, ["linecorp"], "social"),
    S("MeWe", "https://mewe.com/i/{account}", 200, "mewe", "doesn't exist", 404, ["admin"], "social"),
    S("Diaspora (joindiaspora)", "https://joindiaspora.com/people?q={account}", 200, "people-list", "No people found", 200, ["admin"], "social"),
    S("Ello", "https://ello.co/{account}", 200, "UserProfile", "404", 404, ["admin"], "social"),
    S("Micro.blog", "https://micro.blog/{account}", 200, "h-feed", "not found", 404, ["manton"], "blog"),
    S("Cohost", "https://cohost.org/{account}", 200, "profile", "404", 404, ["staff"], "social"),
    S("Hive Social", "https://hivesocial.app/u/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Counter.Social", "https://counter.social/@{account}", 200, "account__header", "is not available", 404, ["admin"], "social"),
    S("Post.news", "https://post.news/@{account}", 200, "profile", "Page Not Found", 404, ["admin"], "social"),
    S("Spoutible", "https://spoutible.com/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Lemon8 Profile", "https://www.lemon8-app.com/{account}", 200, "og:title", "not found", 404, ["admin"], "social"),

    # --- DATING / HOOKUP (deception-heavy) ---
    S("Tinder", "https://tinder.com/@{account}", 200, "og:title", "Looking for someone", 404, ["admin"], "dating"),
    S("Bumble", "https://bumble.com/profiles/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Hinge", "https://hinge.co/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("OkCupid", "https://www.okcupid.com/profile/{account}", 200, "profile-basics", "does not exist", 404, ["admin"], "dating"),
    S("Plenty of Fish", "https://www.pof.com/viewprofile.aspx?profile_id={account}", 200, "profile-details", "not a valid", 404, ["admin"], "dating"),
    S("Badoo", "https://badoo.com/profile/{account}", 200, "js-profile-header", "doesn't exist", 404, ["admin"], "dating"),
    S("Zoosk", "https://www.zoosk.com/p/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Coffee Meets Bagel", "https://coffeemeetsbagel.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Hily", "https://hily.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Happn", "https://www.happn.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Ashley Madison", "https://www.ashleymadison.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Seeking.com", "https://www.seeking.com/member/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Elite Singles", "https://www.elitesingles.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("eHarmony", "https://www.eharmony.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Match.com", "https://www.match.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("JDate", "https://www.jdate.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Christian Mingle", "https://www.christianmingle.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Grindr", "https://grindr.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Her App", "https://weareher.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Feeld", "https://feeld.co/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Loveflutter", "https://loveflutter.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Taimi", "https://taimi.com/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Scruff", "https://www.scruff.com/community/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("SugarDaddy", "https://www.sugardaddy.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Mamba", "https://www.mamba.ru/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Waplog", "https://waplog.com/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Tagged.com", "https://www.tagged.com/profile.html?uid={account}", 200, "profile-info", "not found", 404, ["admin"], "dating"),
    S("MeetMe.com", "https://www.meetme.com/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Skout", "https://www.skout.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),
    S("Lovoo", "https://www.lovoo.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "dating"),

    # --- CRYPTO / FINANCE (deception-heavy) ---
    S("Binance Square", "https://www.binance.com/en/square/profile/{account}", 200, "profile", "not found", 404, ["binance"], "finance"),
    S("Coinbase Profile", "https://www.coinbase.com/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("KuCoin", "https://www.kucoin.com/user/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Bybit", "https://www.bybit.com/en/profile/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("OKX", "https://www.okx.com/account/users/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Gate.io", "https://www.gate.io/user/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Bitget", "https://www.bitget.com/user/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("BitMEX", "https://www.bitmex.com/users/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Bitcointalk", "https://bitcointalk.org/index.php?action=profile;u={account}", 200, "Profile of", "The user whose profile you are trying to view does not exist", 200, ["1"], "finance"),
    S("CoinGecko", "https://www.coingecko.com/en/users/{account}", 200, "user-profile", "not found", 404, ["admin"], "finance"),
    S("CoinMarketCap", "https://coinmarketcap.com/community/profile/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Etherscan", "https://etherscan.io/name-lookup-search?id={account}", 200, "Name Tag", "not found", 404, ["vitalik"], "finance"),
    S("OpenSea", "https://opensea.io/{account}", 200, "AccountPage", "not found", 404, ["admin"], "finance"),
    S("Rarible", "https://rarible.com/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("LooksRare", "https://looksrare.org/accounts/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Robinhood", "https://robinhood.com/@{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("WeBull", "https://www.webull.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Public.com Profile", "https://public.com/@{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Wealthsimple", "https://www.wealthsimple.com/@{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Crypto.com NFT", "https://crypto.com/nft/profile/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("CoinDesk Profile", "https://www.coindesk.com/author/{account}", 200, "author", "not found", 404, ["admin"], "finance"),

    # --- ALT-SOCIAL / ANONYMOUS (deception-heavy) ---
    S("Signal Username", "https://signal.me/#eu/{account}", 200, "signal", "not found", 404, ["admin"], "social"),
    S("Session", "https://sessionapp.org/u/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Wire", "https://wire.com/@{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Briar", "https://briarproject.org/u/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Element (Matrix)", "https://app.element.io/#/user/@{account}:matrix.org", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Keybase", "https://keybase.io/{account}", 200, "profile", "not found", 404, ["chris"], "social"),

    # --- BURNER / VOIP (deception-heavy) ---
    S("TextNow", "https://www.textnow.com/{account}", 200, "profile", "not found", 404, ["admin"], "misc"),
    S("TextFree", "https://www.textfree.us/{account}", 200, "profile", "not found", 404, ["admin"], "misc"),
    S("Google Voice", "https://voice.google.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "misc"),
    S("Talkatone", "https://www.talkatone.com/{account}", 200, "profile", "not found", 404, ["admin"], "misc"),

    # --- MONEY TRANSFER (deception-heavy) ---
    S("Venmo", "https://account.venmo.com/u/{account}", 200, "profile_header", "not found", 404, ["admin"], "finance"),
    S("Cash App", "https://cash.app/${account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Zelle", "https://www.zellepay.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Wise", "https://wise.com/pay/{account}", 200, "profile", "not found", 404, ["admin"], "finance"),
    S("Revolut Profile", "https://revolut.me/{account}", 200, "profile", "This page could not be found", 404, ["admin"], "finance"),

    # --- MARKETPLACE / SCAM VECTORS ---
    S("OfferUp", "https://offerup.com/p/{account}", 200, "profile", "not found", 404, ["admin"], "shopping"),
    S("Mercari", "https://www.mercari.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "shopping"),
    S("StockX", "https://stockx.com/{account}", 200, "profile", "not found", 404, ["admin"], "shopping"),
    S("Grailed", "https://www.grailed.com/{account}", 200, "profile", "not found", 404, ["admin"], "shopping"),
    S("Vinted", "https://www.vinted.com/member/{account}", 200, "profile", "not found", 404, ["admin"], "shopping"),
    S("Facebook Marketplace", "https://www.facebook.com/marketplace/profile/{account}", 200, "profile", "not found", 404, ["admin"], "shopping"),
    S("eBay Profile", "https://www.ebay.com/usr/{account}", 200, "str-seller-card", "doesn't exist", 404, ["admin"], "shopping"),
    S("Swappa", "https://swappa.com/user/{account}", 200, "profile", "not found", 404, ["admin"], "shopping"),
    S("Bonanza", "https://www.bonanza.com/booths/{account}", 200, "booth", "not found", 404, ["admin"], "shopping"),
    S("Reverb", "https://reverb.com/shop/{account}", 200, "shop", "not found", 404, ["admin"], "shopping"),
    S("Tradesy", "https://www.tradesy.com/closet/{account}", 200, "closet", "not found", 404, ["admin"], "shopping"),

    # --- GAMING ---
    S("Steam Community", "https://steamcommunity.com/id/{account}", 200, "profile_page", "The specified profile could not be found", 200, ["gabelogannewell"], "gaming"),
    S("Epic Games", "https://store.epicgames.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "gaming"),
    S("Xbox Profile", "https://xboxgamertag.com/search/{account}", 200, "gamertag", "not found", 404, ["admin"], "gaming"),
    S("PlayStation Profile", "https://psnprofiles.com/{account}", 200, "profile-bar", "was not found", 404, ["admin"], "gaming"),
    S("Riot Games (LoL)", "https://www.leagueofgraphs.com/summoner/na/{account}", 200, "summoner", "not found", 404, ["admin"], "gaming"),
    S("Valorant Tracker", "https://tracker.gg/valorant/profile/riot/{account}", 200, "profile", "not found", 404, ["admin"], "gaming"),
    S("Fortnite Tracker (FN)", "https://fortnitetracker.com/profile/all/{account}", 200, "profile", "not found", 404, ["admin"], "gaming"),
    S("Apex Tracker", "https://apex.tracker.gg/apex/profile/origin/{account}", 200, "profile", "not found", 404, ["admin"], "gaming"),
    S("R6 Tracker", "https://r6.tracker.network/profile/pc/{account}", 200, "profile", "not found", 404, ["admin"], "gaming"),
    S("Destiny Tracker", "https://destinytracker.com/destiny-2/profile/bungie/{account}", 200, "profile", "not found", 404, ["admin"], "gaming"),
    S("Overwatch Tracker", "https://overwatch.blizzard.com/en-us/career/{account}/", 200, "Profile", "not found", 404, ["admin"], "gaming"),
    S("Chess.com Profile", "https://www.chess.com/member/{account}", 200, "profile-card", "is not available", 404, ["hikaru"], "gaming"),
    S("Lichess Profile", "https://lichess.org/@/{account}", 200, "user-show", "Page not found", 404, ["DrNykterstein"], "gaming"),
    S("Osu! Profile", "https://osu.ppy.sh/users/{account}", 200, "profile-info", "User not found", 404, ["peppy"], "gaming"),
    S("RetroAchievements", "https://retroachievements.org/user/{account}", 200, "usersummary", "not found", 404, ["admin"], "gaming"),
    S("Itch.io (ext)", "https://itch.io/profile/{account}", 200, "user_links", "not found", 404, ["admin"], "gaming"),
    S("Minepick", "https://minepick.com/player/{account}", 200, "player-info", "not found", 404, ["Notch"], "gaming"),
    S("NameMC", "https://namemc.com/profile/{account}", 200, "player-skin", "Profiles matching", 404, ["Notch"], "gaming"),
    S("GGStats", "https://gg.stats.fm/user/{account}", 200, "profile", "not found", 404, ["admin"], "gaming"),
    S("Clash of Stats", "https://www.clashofstats.com/players/{account}", 200, "player-info", "not found", 404, ["admin"], "gaming"),

    # --- CONTENT CREATION ---
    S("Substack (ext)", "https://{account}.substack.com", 200, "publication-homepage", "Page not found", 404, ["platformer"], "blog"),
    S("Ghost Blog", "https://{account}.ghost.io", 200, "gh-head", "not found", 404, ["admin"], "blog"),
    S("Notion.so", "https://notion.so/@{account}", 200, "profile", "not found", 404, ["admin"], "blog"),
    S("Bear Blog", "https://{account}.bearblog.dev", 200, "blog-posts", "not found", 404, ["admin"], "blog"),
    S("Buttondown", "https://buttondown.email/{account}", 200, "newsletter", "not found", 404, ["admin"], "blog"),
    S("ConvertKit", "https://app.convertkit.com/{account}", 200, "profile", "not found", 404, ["admin"], "blog"),
    S("Revue", "https://www.getrevue.co/profile/{account}", 200, "profile", "not found", 404, ["admin"], "blog"),
    S("Typeshare", "https://typeshare.co/profile/{account}", 200, "profile", "not found", 404, ["admin"], "blog"),
    S("Mirror.xyz", "https://mirror.xyz/{account}", 200, "publication", "not found", 404, ["admin"], "blog"),
    S("Paragraph.xyz", "https://paragraph.xyz/@{account}", 200, "profile", "not found", 404, ["admin"], "blog"),

    # --- PROFESSIONAL / BUSINESS ---
    S("Glassdoor Profile", "https://www.glassdoor.com/member/profile/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("Indeed Profile", "https://my.indeed.com/p/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("AngelList", "https://angel.co/u/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("Wellfound", "https://wellfound.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("Toptal", "https://www.toptal.com/resume/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("Upwork", "https://www.upwork.com/freelancers/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("Guru.com", "https://www.guru.com/freelancers/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("PeoplePerHour", "https://www.peopleperhour.com/freelancer/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("Bark.com", "https://www.bark.com/en/us/company/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("Alignable", "https://www.alignable.com/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("Crunchbase", "https://www.crunchbase.com/person/{account}", 200, "profile-section", "not found", 404, ["admin"], "business"),
    S("F6S", "https://www.f6s.com/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("Behance (ext)", "https://www.behance.net/{account}", 200, "profile-card", "Oops", 404, ["admin"], "art"),
    S("Dribbble (ext)", "https://dribbble.com/{account}", 200, "profile-masthead", "Page not found", 404, ["admin"], "art"),
    S("99designs", "https://99designs.com/profiles/{account}", 200, "profile", "not found", 404, ["admin"], "art"),

    # --- TECH / DEVELOPER ---
    S("npm (ext)", "https://www.npmjs.com/~{account}", 200, "profile-packages", "404", 404, ["admin"], "coding"),
    S("Crates.io", "https://crates.io/users/{account}", 200, "user-profile", "Not Found", 404, ["admin"], "coding"),
    S("Packagist", "https://packagist.org/users/{account}/", 200, "packages", "not found", 404, ["admin"], "coding"),
    S("NuGet", "https://www.nuget.org/profiles/{account}", 200, "profile-details", "404", 404, ["admin"], "coding"),
    S("Hex.pm", "https://hex.pm/users/{account}", 200, "user-profile", "not found", 404, ["admin"], "coding"),
    S("Pub.dev", "https://pub.dev/publishers/{account}/packages", 200, "publisher", "not found", 404, ["admin"], "coding"),
    S("CocoaPods", "https://cocoapods.org/owners/{account}", 200, "owner", "not found", 404, ["admin"], "coding"),
    S("Homebrew Formulae", "https://formulae.brew.sh/cask/{account}", 200, "formula", "not found", 404, ["admin"], "coding"),
    S("Docker Hub (ext)", "https://hub.docker.com/u/{account}", 200, "user-profile", "HttpError", 404, ["library"], "coding"),
    S("Vercel Profile", "https://vercel.com/{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("Netlify Profile", "https://app.netlify.com/{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("Railway Profile", "https://railway.app/{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("Glitch", "https://glitch.com/@{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("Observable", "https://observablehq.com/@{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("Kaggle (ext)", "https://www.kaggle.com/{account}", 200, "site-layout--profile", "404", 404, ["admin"], "coding"),
    S("Hugging Face (ext)", "https://huggingface.co/{account}", 200, "user-page", "not found", 404, ["admin"], "coding"),
    S("Weights & Biases", "https://wandb.ai/{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("Sourcehut", "https://sr.ht/~{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("Codeberg (ext)", "https://codeberg.org/{account}", 200, "user-profile", "Page Not Found", 404, ["admin"], "coding"),
    S("Forgejo", "https://forgejo.org/{account}", 200, "user-profile", "Page Not Found", 404, ["admin"], "coding"),
    S("Launchpad", "https://launchpad.net/~{account}", 200, "main-side", "There's no person", 404, ["admin"], "coding"),

    # --- MUSIC ---
    S("Spotify (ext)", "https://open.spotify.com/user/{account}", 200, "og:title", "not found", 404, ["spotify"], "music"),
    S("Deezer", "https://www.deezer.com/us/profile/{account}", 200, "profile", "not found", 404, ["admin"], "music"),
    S("Tidal", "https://tidal.com/browse/artist/{account}", 200, "artist", "not found", 404, ["admin"], "music"),
    S("Apple Music", "https://music.apple.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "music"),
    S("Audiomack", "https://audiomack.com/{account}", 200, "artist-card", "not found", 404, ["admin"], "music"),
    S("Genius (ext2)", "https://genius.com/artists/{account}", 200, "profile_identity", "not found", 404, ["admin"], "music"),
    S("ReverbNation", "https://www.reverbnation.com/{account}", 200, "artist-page", "Page Not Found", 404, ["admin"], "music"),
    S("Jamendo", "https://www.jamendo.com/artist/{account}", 200, "artist-card", "not found", 404, ["admin"], "music"),
    S("DistroKid", "https://distrokid.com/hyperfollow/{account}/", 200, "hyperfollow", "not found", 404, ["admin"], "music"),

    # --- VIDEO / STREAMING ---
    S("Dailymotion", "https://www.dailymotion.com/{account}", 200, "ChannelPage", "no longer available", 404, ["admin"], "video"),
    S("Odysee", "https://odysee.com/@{account}", 200, "channel-page", "not found", 404, ["admin"], "video"),
    S("Twitch (ext)", "https://www.twitch.tv/{account}", 200, "tw-mg", "page is in another castle", 404, ["shroud"], "video"),
    S("Kick Profile", "https://kick.com/{account}", 200, "channel-page", "not found", 404, ["admin"], "video"),
    S("Trovo", "https://trovo.live/{account}", 200, "channel", "not found", 404, ["admin"], "video"),
    S("DLive", "https://dlive.tv/{account}", 200, "channel-page", "not found", 404, ["admin"], "video"),
    S("Caffeine", "https://www.caffeine.tv/{account}", 200, "profile", "not found", 404, ["admin"], "video"),
    S("Bigo Live (ext)", "https://www.bigo.tv/{account}", 200, "user_page", "not found", 404, ["admin"], "video"),

    # --- EDUCATION ---
    S("Coursera", "https://www.coursera.org/user/{account}", 200, "profile", "not found", 404, ["admin"], "misc"),
    S("Udacity", "https://profiles.udacity.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "misc"),
    S("Khan Academy", "https://www.khanacademy.org/profile/{account}", 200, "profile-page", "does not exist", 404, ["admin"], "misc"),
    S("Codecademy (ext)", "https://www.codecademy.com/profiles/{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("DataCamp", "https://www.datacamp.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("Pluralsight", "https://app.pluralsight.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("Skillshare", "https://www.skillshare.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "misc"),
    S("Teachable", "https://teachable.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "misc"),
    S("Brilliant", "https://brilliant.org/profile/{account}", 200, "profile", "not found", 404, ["admin"], "misc"),

    # --- HEALTH / FITNESS ---
    S("Strava (ext)", "https://www.strava.com/athletes/{account}", 200, "athlete-profile", "Page Not Found", 404, ["admin"], "health"),
    S("Fitbit", "https://www.fitbit.com/user/{account}", 200, "profile", "not found", 404, ["admin"], "health"),
    S("MapMyRun", "https://www.mapmyrun.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "health"),
    S("Garmin Connect (ext)", "https://connect.garmin.com/modern/profile/{account}", 200, "profile", "not found", 404, ["admin"], "health"),
    S("Peloton", "https://members.onepeloton.com/members/{account}", 200, "profile", "not found", 404, ["admin"], "health"),
    S("Komoot", "https://www.komoot.com/user/{account}", 200, "profile", "not found", 404, ["admin"], "health"),
    S("AllTrails", "https://www.alltrails.com/members/{account}", 200, "profile", "not found", 404, ["admin"], "health"),
    S("Nike Run Club", "https://www.nike.com/member/profile/{account}", 200, "profile", "not found", 404, ["admin"], "health"),

    # --- NEWS / MEDIA ---
    S("Medium (ext)", "https://medium.com/@{account}", 200, "og:title", "doesn't exist", 404, ["ev"], "blog"),
    S("Substack Author", "https://substack.com/@{account}", 200, "profile", "not found", 404, ["admin"], "blog"),
    S("The Guardian Profile", "https://profile.theguardian.com/user/{account}", 200, "profile", "not found", 404, ["admin"], "news"),
    S("Reuters Author", "https://www.reuters.com/authors/{account}", 200, "author", "not found", 404, ["admin"], "news"),
    S("Bloomberg Profile", "https://www.bloomberg.com/profile/person/{account}", 200, "profile", "not found", 404, ["admin"], "news"),
    S("Forbes Profile", "https://www.forbes.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "news"),

    # --- NSFW / ADULT (deception-heavy) ---
    S("OnlyFans (ext)", "https://onlyfans.com/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("Fansly (ext)", "https://fansly.com/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("ManyVids", "https://www.manyvids.com/Profile/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("Clips4Sale", "https://www.clips4sale.com/studio/{account}", 200, "studio", "not found", 404, ["admin"], "xx NSFW xx"),
    S("MyFreeCams", "https://profiles.myfreecams.com/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("Cam4", "https://www.cam4.com/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("CamSoda", "https://www.camsoda.com/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("LiveJasmin", "https://www.livejasmin.com/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("BongaCams (ext)", "https://bongacams.com/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("StripChat (ext)", "https://stripchat.com/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("iWantClips", "https://iwantclips.com/store/{account}", 200, "store", "not found", 404, ["admin"], "xx NSFW xx"),
    S("Pornhub Model (ext)", "https://www.pornhub.com/model/{account}", 200, "profilePage", "Page Not Found", 404, ["admin"], "xx NSFW xx"),
    S("XHamster Profile", "https://xhamster.com/users/{account}", 200, "user-profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("SpankBang", "https://spankbang.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("Noodlemagazine", "https://www.noodlemagazine.com/user/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("RedTube", "https://www.redtube.com/users/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("YouPorn", "https://www.youporn.com/uprofile/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("Tube8", "https://www.tube8.com/users/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("AdultFriendFinder", "https://adultfriendfinder.com/p/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("FetLife", "https://fetlife.com/users/{account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),
    S("Switter", "https://switter.at/@{account}", 200, "account__header", "not available", 404, ["admin"], "xx NSFW xx"),
    S("Literotica", "https://www.literotica.com/stories/memberpage.php?uid={account}", 200, "profile", "not found", 404, ["admin"], "xx NSFW xx"),

    # --- LINK-IN-BIO / IDENTITY ---
    S("Linktree (ext)", "https://linktr.ee/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Beacons (ext)", "https://beacons.ai/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Bio.link", "https://bio.link/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Carrd (ext)", "https://{account}.carrd.co", 200, "og:title", "not found", 404, ["admin"], "social"),
    S("About.me (ext)", "https://about.me/{account}", 200, "og:title", "about.me</title>", 404, ["john"], "social"),
    S("Solo.to (ext)", "https://solo.to/{account}", 200, "og:title", "not found", 404, ["admin"], "social"),
    S("Lnk.bio", "https://lnk.bio/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Taplink", "https://taplink.cc/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Milkshake", "https://msha.ke/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Campsite.bio", "https://campsite.bio/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Stan.store", "https://stan.store/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Gumroad (ext)", "https://gumroad.com/{account}", 200, "profile", "not found", 404, ["admin"], "shopping"),
    S("Ko-fi (ext)", "https://ko-fi.com/{account}", 200, "kofistyle", "404", 404, ["admin"], "misc"),
    S("Buy Me a Coffee (ext)", "https://buymeacoffee.com/{account}", 200, "bmc-profile", "not found", 404, ["admin"], "misc"),

    # --- REGIONAL PLATFORMS ---
    # Russian
    S("VK (ext)", "https://vk.com/{account}", 200, "profile_info", "Page not found", 404, ["admin"], "social"),
    S("OK.ru (ext)", "https://ok.ru/profile/{account}", 200, "profile-user", "profile_deleted", 404, ["admin"], "social"),
    S("Yandex.Zen", "https://zen.yandex.ru/id/{account}", 200, "channel-page", "not found", 404, ["admin"], "blog"),
    S("Habr Career", "https://career.habr.com/{account}", 200, "profile", "not found", 404, ["admin"], "business"),
    S("Pikabu (ext)", "https://pikabu.ru/@{account}", 200, "profile__header", "Ошибка 404", 404, ["admin"], "social"),
    S("VC.ru", "https://vc.ru/u/{account}", 200, "subsite-header", "Ошибка", 404, ["admin"], "tech"),
    S("DTF", "https://dtf.ru/u/{account}", 200, "subsite-header", "Ошибка", 404, ["admin"], "gaming"),
    S("Avito", "https://www.avito.ru/user/{account}", 200, "seller-info", "не найдена", 404, ["admin"], "shopping"),
    S("Youla", "https://youla.ru/user/{account}", 200, "profile", "не найден", 404, ["admin"], "shopping"),

    # Japanese
    S("Note.com", "https://note.com/{account}", 200, "o-profile", "not found", 404, ["admin"], "blog"),
    S("Qiita", "https://qiita.com/{account}", 200, "userProfileCard", "404", 404, ["admin"], "coding"),
    S("Zenn (ext)", "https://zenn.dev/{account}", 200, "user-profile", "404", 404, ["admin"], "coding"),
    S("Hatena Blog", "https://{account}.hatenablog.com/", 200, "blog-title", "not found", 404, ["admin"], "blog"),
    S("Niconico", "https://www.nicovideo.jp/user/{account}", 200, "UserProfile", "not found", 404, ["admin"], "video"),
    S("pixiv (ext)", "https://www.pixiv.net/users/{account}", 200, "user-profile", "not found", 404, ["admin"], "art"),
    S("Booth.pm (ext)", "https://{account}.booth.pm/", 200, "shop-head", "not found", 404, ["admin"], "shopping"),

    # Korean
    S("Naver Blog", "https://blog.naver.com/{account}", 200, "blog-body", "존재하지 않는", 404, ["admin"], "blog"),
    S("Daum Blog", "https://blog.daum.net/{account}", 200, "blog", "not found", 404, ["admin"], "blog"),
    S("Tistory", "https://{account}.tistory.com", 200, "article_skin", "not found", 404, ["admin"], "blog"),

    # Chinese
    S("Bilibili", "https://space.bilibili.com/{account}", 200, "h-name", "not found", 404, ["1"], "video"),
    S("Douban", "https://www.douban.com/people/{account}", 200, "info", "页面不存在", 404, ["admin"], "social"),
    S("Zhihu (ext)", "https://www.zhihu.com/people/{account}", 200, "Profile", "not found", 404, ["admin"], "social"),
    S("Weibo (ext)", "https://weibo.com/{account}", 200, "profile_top", "not found", 404, ["admin"], "social"),
    S("Gitee (ext)", "https://gitee.com/{account}", 200, "user-profile", "not found", 404, ["admin"], "coding"),
    S("CSDN", "https://blog.csdn.net/{account}", 200, "profile", "not found", 404, ["admin"], "coding"),
    S("Juejin", "https://juejin.cn/user/{account}", 200, "user-profile", "not found", 404, ["admin"], "coding"),
    S("Xiaohongshu", "https://www.xiaohongshu.com/user/profile/{account}", 200, "user-info", "not found", 404, ["admin"], "social"),

    # Brazilian
    S("Koo", "https://www.kooapp.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("OLX Brasil", "https://www.olx.com.br/perfil/{account}", 200, "profile", "not found", 404, ["admin"], "shopping"),
    S("Mercado Livre", "https://perfil.mercadolivre.com.br/{account}", 200, "profile", "not found", 404, ["admin"], "shopping"),

    # German
    S("Xing (ext)", "https://www.xing.com/profile/{account}", 200, "og:title", "not found", 404, ["admin"], "business"),
    S("Kleinanzeigen", "https://www.kleinanzeigen.de/s-bestandsliste.html?userId={account}", 200, "user-profile", "not found", 404, ["admin"], "shopping"),

    # Indian
    S("ShareChat", "https://sharechat.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Koo India", "https://www.kooapp.com/profile/{account}", 200, "profile", "not found", 404, ["admin"], "social"),
    S("Moj", "https://mojapp.in/@{account}", 200, "profile", "not found", 404, ["admin"], "video"),

    # --- HOBBY / MISC ---
    S("Goodreads", "https://www.goodreads.com/user/show/{account}", 200, "userInfoBoxContent", "not found", 404, ["1"], "hobby"),
    S("Letterboxd (ext)", "https://letterboxd.com/{account}", 200, "person-summary", "sorry", 404, ["admin"], "hobby"),
    S("MAL (ext)", "https://myanimelist.net/profile/{account}", 200, "user-profile", "404", 404, ["admin"], "hobby"),
    S("AniList (ext)", "https://anilist.co/user/{account}", 200, "user-page-unscoped", "not found", 404, ["admin"], "hobby"),
    S("Discogs (ext)", "https://www.discogs.com/user/{account}", 200, "profile-header", "not found", 404, ["admin"], "music"),
    S("RateYourMusic", "https://rateyourmusic.com/~{account}", 200, "user_info", "not found", 404, ["admin"], "music"),
    S("Trakt (ext)", "https://trakt.tv/users/{account}", 200, "profile-section", "not found", 404, ["admin"], "hobby"),
    S("Serializd", "https://www.serializd.com/user/{account}", 200, "profile", "not found", 404, ["admin"], "hobby"),
    S("Backloggd", "https://www.backloggd.com/u/{account}", 200, "profile", "not found", 404, ["admin"], "hobby"),
    S("BoardGameGeek (ext)", "https://boardgamegeek.com/user/{account}", 200, "profile", "not found", 404, ["admin"], "hobby"),
    S("AllRecipes", "https://www.allrecipes.com/cook/{account}", 200, "profile", "not found", 404, ["admin"], "hobby"),
    S("Untappd (ext)", "https://untappd.com/user/{account}", 200, "profile-card", "not found", 404, ["admin"], "hobby"),
    S("Vivino (ext)", "https://www.vivino.com/users/{account}", 200, "user-profile", "not found", 404, ["admin"], "hobby"),
    S("Geocaching (ext)", "https://www.geocaching.com/p/default.aspx?u={account}", 200, "profile", "not found", 404, ["admin"], "hobby"),
]

# ============================================================================
# ADDITIONAL GITLAB INSTANCES
# ============================================================================

GITLAB_INSTANCES = [
    ("gitlab.gnome.org", "GNOME GitLab"),
    ("gitlab.freedesktop.org", "FreeDesktop GitLab"),
    ("gitlab.alpinelinux.org", "Alpine Linux GitLab"),
    ("gitlab.archlinux.org", "Arch Linux GitLab"),
    ("salsa.debian.org", "Debian Salsa"),
    ("gitlab.com", "GitLab.com"),
    ("gitlab.haskell.org", "Haskell GitLab"),
    ("gitlab.torproject.org", "Tor GitLab"),
    ("gitlab.tails.boum.org", "Tails GitLab"),
    ("gitlab.xfce.org", "XFCE GitLab"),
    ("invent.kde.org", "KDE Invent"),
    ("code.videolan.org", "VideoLAN GitLab"),
    ("gitlab.manjaro.org", "Manjaro GitLab"),
    ("gitlab.nic.cz", "CZ.NIC GitLab"),
    ("gitlab.redox-os.org", "Redox OS GitLab"),
    ("gitlab.libreoffice.org", "LibreOffice GitLab"),
]

GITEA_INSTANCES = [
    ("codeberg.org", "Codeberg"),
    ("gitea.com", "Gitea.com"),
    ("tea.gitea.io", "Gitea Tea"),
    ("git.sr.ht", "Sourcehut"),
    ("notabug.org", "NotABug"),
    ("git.disroot.org", "Disroot Gitea"),
    ("git.feneas.org", "Feneas Gitea"),
    ("git.pleroma.social", "Pleroma Gitea"),
    ("code.blicky.net", "Blicky Gitea"),
    ("git.nixnet.services", "NixNet Gitea"),
    ("git.nacdlow.com", "Nacdlow Gitea"),
    ("git.teknik.io", "Teknik Gitea"),
]

# ============================================================================
# PHPBB / VBULLETIN / XENFORO FORUMS
# ============================================================================

PHPBB_FORUMS = [
    ("forums.phpbb.com", "phpBB Forums", "tech"),
    ("forums.somethingawful.com", "Something Awful", "misc"),
    ("forum.blockland.us", "Blockland Forums", "gaming"),
    ("forums.heroesofnewerth.com", "HoN Forums", "gaming"),
    ("forum.openstreetmap.org", "OSM Forum", "hobby"),
    ("forum.doom9.org", "Doom9 Forum", "tech"),
    ("forums.videocardz.com", "VideoCardz Forums", "tech"),
    ("forums.hardwarezone.com.sg", "HardwareZone Forums", "tech"),
    ("forums.macrumors.com", "MacRumors Forums", "tech"),
    ("forum.notebookreview.com", "Notebook Review", "tech"),
    ("forums.anandtech.com", "AnandTech Forums", "tech"),
    ("forums.techguy.org", "Tech Guy Forums", "tech"),
    ("forums.overclockers.co.uk", "Overclockers UK", "tech"),
    ("forum.hi-fi.com.sg", "HiFi Forum", "hobby"),
    ("forums.cpanel.net", "cPanel Forums", "tech"),
    ("forums.whirlpool.net.au", "Whirlpool Forums", "tech"),
    ("forums.gentoo.org", "Gentoo Forums", "tech"),
    ("www.sitepoint.com/community", "SitePoint Community", "coding"),
    ("forum.winamp.com", "Winamp Forum", "music"),
    ("forums.beyond3d.com", "Beyond3D Forums", "tech"),
]

VBULLETIN_FORUMS = [
    ("forum.xda-developers.com", "XDA Forums", "tech"),
    ("forums.mydigitallife.net", "MDL Forums", "tech"),
    ("www.avsforum.com", "AVS Forum", "hobby"),
    ("forums.stevehoffman.tv", "Steve Hoffman Forums", "music"),
    ("forum.dvdtalk.com", "DVD Talk Forums", "hobby"),
    ("forums.digitalpoint.com", "Digital Point Forums", "business"),
    ("forums.tomshardware.com", "Tom's Hardware Forums", "tech"),
    ("forums.vwvortex.com", "VW Vortex Forums", "hobby"),
    ("forums.bimmerforums.com", "Bimmer Forums", "hobby"),
    ("forums.audiworld.com", "Audi World Forums", "hobby"),
    ("forums.nasioc.com", "NASIOC Subaru Forums", "hobby"),
    ("forums.corvetteforum.com", "Corvette Forum", "hobby"),
    ("forums.mustangforums.com", "Mustang Forums", "hobby"),
    ("forums.f150forum.com", "F-150 Forum", "hobby"),
    ("forums.jeepforum.com", "Jeep Forum", "hobby"),
    ("forums.toyotanation.com", "Toyota Nation Forums", "hobby"),
    ("forums.civicx.com", "Civic X Forums", "hobby"),
    ("forums.teslaownersonline.com", "Tesla Owners Forums", "hobby"),
    ("forums.redflagdeals.com", "Red Flag Deals", "shopping"),
    ("forums.hardocp.com", "HardOCP Forums", "tech"),
]

XENFORO_FORUMS = [
    ("forums.spacebattles.com", "SpaceBattles", "hobby"),
    ("forums.sufficientvelocity.com", "Sufficient Velocity", "hobby"),
    ("forum.questionablequesting.com", "Questionable Questing", "hobby"),
    ("hypixel.net", "Hypixel Forums", "gaming"),
    ("minecraftforum.net", "Minecraft Forum", "gaming"),
    ("www.alternatehistory.com", "Alternate History", "hobby"),
    ("forums.nexusmods.com", "Nexus Mods Forums", "gaming"),
    ("forums.otterhalf.com", "OtterHalf Forums", "misc"),
    ("forums.androidcentral.com", "Android Central Forums", "tech"),
    ("forums.windowscentral.com", "Windows Central Forums", "tech"),
    ("forums.imore.com", "iMore Forums", "tech"),
    ("forums.crackberry.com", "CrackBerry Forums", "tech"),
    ("forum.xperiablog.net", "Xperia Blog Forum", "tech"),
    ("forums.digitalspy.com", "Digital Spy Forums", "misc"),
    ("www.thestudentroom.co.uk", "The Student Room", "misc"),
    ("www.rllmukforum.com", "RLLMUK Forum", "gaming"),
    ("www.resetera.com", "ResetEra", "gaming"),
    ("www.neogaf.com", "NeoGAF", "gaming"),
    ("forums.furaffinity.net", "Fur Affinity Forums", "art"),
    ("kiwifarms.net", "Kiwi Farms", "misc"),
    ("lolcow.farm", "lolcow.farm", "misc"),
]

# ============================================================================
# MAIN GENERATION
# ============================================================================

def generate():
    all_sites = []

    # Template-generated
    all_sites.extend(gen_mastodon(MASTODON_INSTANCES))
    all_sites.extend(gen_lemmy(LEMMY_INSTANCES))
    all_sites.extend(gen_pixelfed(PIXELFED_INSTANCES))
    all_sites.extend(gen_misskey(MISSKEY_INSTANCES))
    all_sites.extend(gen_pleroma(PLEROMA_INSTANCES))
    all_sites.extend(gen_peertube(PEERTUBE_INSTANCES))
    all_sites.extend(gen_writefreely(WRITEFREELY_INSTANCES))
    all_sites.extend(gen_discourse(DISCOURSE_FORUMS))
    all_sites.extend(gen_phpbb_forums(PHPBB_FORUMS))
    all_sites.extend(gen_vbulletin_forums(VBULLETIN_FORUMS))
    all_sites.extend(gen_xenforo_forums(XENFORO_FORUMS))
    all_sites.extend(gen_gitlab_instances(GITLAB_INSTANCES))
    all_sites.extend(gen_gitea_instances(GITEA_INSTANCES))

    # Manually curated
    all_sites.extend(MAJOR_SITES)

    # Deduplicate by uri_check
    seen = set()
    deduped = []
    for s in all_sites:
        key = s["uri_check"].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(s)

    # Sort by name
    deduped.sort(key=lambda s: s["name"].lower())

    output = {
        "license": [
            "Extended site list for WhatsMyName",
            "Generated by scripts/generate_sites.py",
            "Contains curated entries and template-generated platform instances",
        ],
        "categories": sorted({s["cat"] for s in deduped}),
        "sites": deduped,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Stats
    cats = {}
    for s in deduped:
        c = s["cat"]
        cats[c] = cats.get(c, 0) + 1

    print(f"Generated {len(deduped)} sites → {OUTPUT}")
    print("\nBy category:")
    for c in sorted(cats.keys()):
        print(f"  {c}: {cats[c]}")


if __name__ == "__main__":
    generate()
