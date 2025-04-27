document.addEventListener('DOMContentLoaded', function () {
    var player = videojs('my-video');

    player.ready(function () {
        var audioTracks = player.audioTracks();
        
        if (audioTracks.length > 1) {
            var controlBar = player.getChild('controlBar');
            var fullscreenToggle = controlBar.getChild('fullscreenToggle');

            var languageMenuButton = document.createElement('div');
            languageMenuButton.className = 'vjs-control vjs-button vjs-language-button';
            languageMenuButton.innerHTML = '<span class="vjs-icon-placeholder">🌐</span>';

            languageMenuButton.style.cursor = 'pointer';
            languageMenuButton.style.padding = '0 10px';
            languageMenuButton.title = "Change Audio Language";

            fullscreenToggle.el().parentNode.insertBefore(languageMenuButton, fullscreenToggle.el());

            languageMenuButton.addEventListener('click', function () {
                var options = '';
                for (var i = 0; i < audioTracks.length; i++) {
                    options += `${i + 1}. ${audioTracks[i].label}\n`;
                }
                var choice = prompt(`Select Audio Track:\n\n${options}`);
                if (choice !== null) {
                    var selected = parseInt(choice) - 1;
                    if (selected >= 0 && selected < audioTracks.length) {
                        for (var j = 0; j < audioTracks.length; j++) {
                            audioTracks[j].enabled = (j === selected);
                        }
                    }
                }
            });
        }
    });
});
