dojo.provide("sfdr.pages");

dojo.require("dojo.hash");
dojo.require("cvdj.capstring");
dojo.require("dojo.fx");

c = {
    svs : [ {
        type : "twitter",
        name : "C4Vi",
        avatar : "http://a2.twimg.com/profile_images/1278412600/IMG_0197_3_normal.jpg"
    }, {
        type : "twitter",
        name : "CVis500d",
        avatar : "http://a0.twimg.com/profile_images/1315998557/DSC00678_-_Version_2_normal.jpg"
    }, ],
    snr : [ {
        type : "bitly",
        name : "christoffervi"
    } ],
    fds : [ {
        name : "500d",
        id : 3
    } ]
};

dojo.declare("sfdr.pages.page", null, {
    _precon : function() {
        this.f = dojo.create("div", null, dojo.byId("main"));
        this.f.style.display = "none";
    },
    _postcon : function() {

    },
    destroy : function() {
        dojo.destroy(this.f);
    }
});

dojo.declare("sfdr.pages.form", sfdr.pages.page, {
    url : "/ajax/dummy/{id}/callback.json"
});

dojo.declare("sfdr.pages.loading", sfdr.pages.page, {
    constructor : function(data) {
        this._precon();
        dojo.create("img", {
            src : "/static/loader.gif"
        }, dojo.create("div", {
            style : "text-align: center"
        }, this.f));
        this._postcon();
    }
});

dojo.declare("sfdr.pages.dashboard", sfdr.pages.page, {
    constructor : function(data) {
        this._precon();
        this.svs = dojo.create("div", null, dojo.create("div", {
            "class" : "links"
        }, this.f));
        dojo.create("div", {
            "class" : "head",
            innerHTML : "Services"
        }, this.svs);
        for (s in data.svs) {
            sv = data.svs[s];
            l = dojo.create("div", {
                "class" : "link"
            }, this.svs);
            dojo.create("img", {
                "class" : "avatar",
                src : sv.avatar
            }, l);
            dojo.create("div", {
                "class" : "text",
                innerHTML : sv.type.capitalize() + ": " + sv.name
            }, l);
        }

        var links = dojo.create("div", null, dojo.create("div", {
            "class" : "links"
        }, this.f));
        dojo.create("div", {
            "class" : "head",
            innerHTML : "Shorteners"
        }, links);
        for (s in data.snr) {
            sn = data.snr[s];
            l = dojo.create("div", {
                "class" : "link"
            }, links);
            dojo.create("div", {
                "class" : "text",
                innerHTML : sn.type.capitalize() + ": " + sn.name
            }, l);
        }

        var links = dojo.create("div", null, dojo.create("div", {
            "class" : "links"
        }, this.f));
        dojo.create("div", {
            "class" : "head",
            innerHTML : "Feeds"
        }, links);
        for (s in data.fds) {
            sn = data.fds[s];
            var l = dojo.create("div", { "class" : "link" }, links);
            dojo.create("div", {"class" : "text",innerHTML : sn.name}, l);
            dojo.connect(l,"onclick", data.fds[s], this.gotoFeed)
        }
        this._postcon();
    },
    gotoFeed: function(){
        dojo.hash("!/feed/"+this.name,true);
    }
});

dojo.declare("sfdr.pages.controller", null, {
    constructor : function() {
        dojo.subscribe("/dojo/hashchange", this, this.change);
        this.loader = new sfdr.pages.loading();
        this.shloader();
        this.current = new sfdr.pages.dashboard(c);
        this.showpage(this.current.f);
    },
    change : function(hash) {
        this.hidepage(this.current.f);
        console.log("Yup, event caught")
    },
    shloader: function(){
        this.loader.f.style.height = "";
        this.loader.f.style.display = "block";
        this.loader.o = dojo.fadeOut({node : this.loader.f, duration:100,onEnd:this.hideld()} );
        this.loader.i = dojo.fadeIn({node : this.loader.f, duration:100,beforeBegin:this.shld()} );
    },
    showpage : function(o) {
        var anim = dojo.fx.wipeIn({
            node : o,
            duration : 1000
        });
        dojo.fx.chain([this.loader.o, anim]).play();
    },
    hidepage : function(o) {
        var anim = dojo.fx.wipeOut({
            node : o,
            duration : 1000
        });
        dojo.fx.chain([anim, this.loader.i]).play();
    },
    hideld: function(){
        this.loader.f.style.display = "none";
    },
    shld: function(){
        this.loader.f.style.display = "block";
    }
});

/*
 * window.authDone = function(){ dojo.destroy(dojo.byId("authFrame")); delete
 * window.authDone; }
 */

function iniT() {
    d = sfdr.pages.controller();
}
dojo.addOnLoad(iniT);
