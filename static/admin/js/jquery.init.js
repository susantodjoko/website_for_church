/*global jQuery:false*/
'use strict';
/* Override of Django's own admin/js/jquery.init.js (shadowed here via
   STATICFILES_DIRS, which the FileSystemFinder checks before the
   AppDirectoriesFinder that would otherwise serve Django's copy).

   Django's original only exposes jQuery as django.jQuery, deliberately
   wiping window.$ and window.jQuery via noConflict(true) to avoid
   polluting the global namespace. django-summernote's 'lite' theme
   (used with iframe: False) ships plugin scripts (jquery.ui.widget.js,
   jquery.iframe-transport.js, jquery.fileupload.js, summernote-lite.min.js)
   that are loaded as plain <script> tags and expect a real global
   jQuery/$ to already exist — without it they throw immediately on load.
   This restores those globals while keeping django.jQuery working too. */
window.django = {jQuery: jQuery.noConflict(true)};
window.jQuery = window.$ = django.jQuery;
