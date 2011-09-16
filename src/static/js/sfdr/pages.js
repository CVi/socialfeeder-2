dojo.provide("sfdr.pages");

dojo.require("dojo.hash");
dojo.require("cvdj.capstring");
dojo.require("cvdj.Cache")
dojo.require("dojo.fx");

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
        dojo.create("img", { src : "/static/loader.gif" }, dojo.create("div", { style : "text-align: center"}, this.f));
        this._postcon();
    }
});

dojo.declare("sfdr.pages.dashboard", sfdr.pages.page, {
    constructor : function(data) {
        this._precon();
        this.svs = dojo.create("div", null, dojo.create("div", {"class" : "links"}, this.f));
        dojo.create("div", {"class" : "head", innerHTML : "Services" }, this.svs);
        for (s in data.svs) {
            var sv = data.svs[s];
            var l = dojo.create("div", {"class" : "link"}, this.svs);
            dojo.create("img", {"class" : "avatar", src : sv.avatar}, l);
            dojo.create("div", { "class" : "text", innerHTML : sv.type.capitalize() + ": " + sv.name}, l);
        }

        var links = dojo.create("div", null, dojo.create("div", {"class" : "links"}, this.f));
        dojo.create("div", { "class" : "head", innerHTML : "Shorteners"}, links);
        for (s in data.snr) {
            var sn = data.snr[s];
            var l = dojo.create("div", {"class" : "link"}, links);
            dojo.create("div", {"class" : "text",innerHTML : sn.type.capitalize() + ": " + sn.name}, l);
        }

        var links = dojo.create("div", null, dojo.create("div", {"class" : "links"}, this.f));
        dojo.create("div", {"class" : "head",innerHTML : "Feeds"}, links);
        for (s in data.fds) {
            var sn = data.fds[s];
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

dojo.declare("sfdr.pages.feed", sfdr.pages.page, {
	constructor: function(data){
        this._precon();
		this.data = data.data;
		this.shorteners = data.shorteners;
		this.formats = data.formats;
		this.fons = data.fons;
		this.cfes = data.cfes;
		this.svs = data.svs;
		this.display();
        this._postcon();
	},
	display: function(){
		this.disp = dojo.create("div", {}, this.f);
        var u = dojo.create("ul",{}, this.disp);
        var l = dojo.create("li", {}, u);
        dojo.create("span", {innerHTML: "Name: ", style:{"margin-right":"5px"}}, l);
        dojo.create("span", {innerHTML: this.data.name}, l);

        var l = dojo.create("li", {}, u);
        dojo.create("span", {innerHTML: "Feed URL: ", style:{"margin-right":"5px"}}, l);
        dojo.create("span", {innerHTML: this.data.feed}, l);

        var l = dojo.create("li", {}, u);
        dojo.create("span", {innerHTML: "URL Shortener: ", style:{"margin-right":"5px"}}, l);
        dojo.create("span", {innerHTML: this.shorteners[this.data.shortener]}, l);

        var l = dojo.create("ul", {}, dojo.create("li", {innerHTML:"Services:<br />"}, u));
        for (i in this.data.svs){
        	dojo.create("li", {innerHTML:this.svs[this.data.svs[i]]}, l);
        }

	}
});

dojo.declare("sfdr.pages.controller", null, {
    constructor : function() {
        dojo.subscribe("/dojo/hashchange", this, this.change);
        this.loader = new sfdr.pages.loading();
        this.shloader();
        this.manager = new sfdr.pages.manager();
        this.change(dojo.hash());
    },
    change : function(hash) {
    	if (this.current){
	        this.hidepage(this.current.f);
    	}
        hash = hash.substring(2).split("/");
        this.current = this.manager.fetch(hash[0], hash[1]);
        this.showpage(this.current.f)
        console.log("hash has changed");
        console.log(hash);
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

dojo.declare("sfdr.pages.manager", null, {
	constructor: function(){
		console.log("Manager Loaded");
		this.cache = new cvdj.Cache();
	},
	fetch: function(type, id){
		var d = null;
		console.log("Fetching")
		d = this.cache.get(type+"/"+id)
		if(d){
			return d
		}
		else{
			switch(type){
				case "feed":
				    var req = "/static/feed.json";
				    var p = sfdr.pages.feed;
				    break;
				 
			    default:
			    	var req = "/static/dashboard.json";
			    	var p = sfdr.pages.dashboard;
			}
			if (req != undefined){
				var ds = null;
				dojo.xhrGet({
				    url:req,
    				handleAs:"json",
    				sync: true,
    				load: function(data){
        				ds = data;
				    }
				});
				console.log(ds);
				return p(ds);
			}
		}
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
