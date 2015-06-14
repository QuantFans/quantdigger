/**
 * Justboil.me - a TinyMCE image upload plugin
 * jbimages/js/dialog-v4.js
 *
 * Released under Creative Commons Attribution 3.0 Unported License
 *
 * License: http://creativecommons.org/licenses/by/3.0/
 * Plugin info: http://justboil.me/
 * Author: Viktor Kuzhelnyi
 *
 * Version: 2.3 released 23/06/2013
 */
 
var jbImagesDialog = {
	
	resized : false,
	iframeOpened : false,
	timeoutStore : false,
	
	inProgress : function() {
		this.timeoutStore = window.setTimeout(function(){
			document.getElementById("error_info").innerHTML = 'This is taking longer than usual.' + '<br />' + 'An error may have occurred.';
		}, 20000);

	},
	
	showIframe : function() {
		if (this.iframeOpened == false)
		{
			document.getElementById("upload_target").className = 'upload_target_visible';
			// tinyMCEPopup.editor.windowManager.resizeBy(0, 190, tinyMCEPopup.id);
			this.iframeOpened = true;
		}
	},
	
	uploadFinish : function(result) {
			
        console.log(result);
			var w = this.getWin();
			tinymce = w.tinymce;
            console.log(w);
		
			tinymce.EditorManager.activeEditor.insertContent('<img src="' + result +'">');
			
			this.close();
	},
	
	getWin : function() {
		return (!window.frameElement && window.dialogArguments) || opener || parent || top;
	},
	
	close : function() {
		var t = this;

		// To avoid domain relaxing issue in Opera
		function close() {
			tinymce.EditorManager.activeEditor.windowManager.close(window);
			tinymce = tinyMCE = t.editor = t.params = t.dom = t.dom.doc = null; // Cleanup
		};

		if (tinymce.isOpera)
			this.getWin().setTimeout(close, 0);
		else
			close();
	}

};
