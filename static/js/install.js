/**
 * Digital Dukan PWA Installer Logic (v9.5)
 */

(function () {
    let deferredPrompt;
    const installBanner = document.getElementById('pwa-install-banner');
    const installTrigger = document.getElementById('pwa-install-trigger');
    const closeBtn = document.getElementById('pwa-close-btn');

    // 0. Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone) {
        console.log("PWA: Running in app mode.");
        return; 
    }

    // 1. Listen for install availability
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        if (installBanner) installBanner.classList.add('active');
        console.log("PWA: Install Prompt Ready");
    });

    // 2. Handle Install Action
    if (installTrigger) {
        installTrigger.addEventListener('click', () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((result) => {
                    if (result.outcome === 'accepted') {
                        if (installBanner) installBanner.classList.remove('active');
                    }
                    deferredPrompt = null;
                });
            } else {
                // Fallback for iOS or cases where prompt isn't ready
                alert("To install: Tap the 'Share' icon and then 'Add to Home Screen'.");
            }
        });
    }

    // 3. Close Logic
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
             if (installBanner) installBanner.classList.remove('active');
        });
    }

    // 4. Auto-hide when successful
    window.addEventListener('appinstalled', () => {
        if (installBanner) installBanner.classList.remove('active');
    });

})();
