var DJMARKUP = {
    $: jQuery,

    load_css: function(type) {
        var url = _markup_media_prefix + 'markitup/sets/' + type + '/style.css';
        if ($('link[@rel*=style][href='+url+']').length == 0)
            $('<link>')
                .attr({type: 'text/css', href: url, rel: 'stylesheet', media: 'screen'})
                .appendTo('head');
    },

    init_field: function(name) {
        $('#id_'+name+'_markup_type').change(function () {
            DJMARKUP.markitup(name);
        });
        DJMARKUP.markitup(name);
    },

    do_markitup: function($ta, type) {
        var ctype = type.substring(0, 1).toUpperCase() + type.substring(1, type.length);
        DJMARKUP.load_css(type);
        eval('my' + ctype + 'Settings');
        //return;
        $ta.markItUp(eval('my' + ctype + 'Settings'));

        var parent = $ta.parents('[class=markItUp]'),
            height = $ta.height() + 30;
        $ta.after('<style>#'+parent.attr('id')+' .markItUpPreviewFrame {height:'+height+'px}</style>');
    },

    markitup: function(name) {
        var $ta = $('#id_'+name),
            type = $('#id_'+name+'_markup_type').val();

        $ta.markItUpRemove();
        $.getScript(
            _markup_media_prefix + 'markitup/sets/' + type + '/set.js',
            function () {
                DJMARKUP.do_markitup($ta, type);
            }
        );
    }
};
