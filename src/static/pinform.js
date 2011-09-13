dojo.declare("sfdr.form.field", null,{
		name: null,
		title: null,
		ph: null,
		field: "input",
		type: "hidden",
		object: null,
		wrapper: null,
	    constructor: function(name, title, placeholder){
	        // summary:
	        //         Generic form field, intended as a abstract class
	        // name: string
	        //         Name of the field
	        // title: string
	        //         Human readable name of field (usually used as field label)
	        // placeholder: string
	        //         Input placeholder, text that remains within the input fields
	        //         before the user fills them out.
	    	this.name = name;
	    	this.title = title;
	    	this.ph = placeholder;
	    },
	    render: function(parent){
	        // summary:
	        //         Renders the field into DOM
	        // parent: DOM node
	        //         Parent DOM node
	    	this.wrapper = dojo.create("li", null, parent);
	    	dojo.create("span", {innerHTML:this.title}, this.wrapper);
	    	this.object = dojo.create("input", {name:this.name, type:this.type, placeholder:this.ph}, this.wrapper);
	    },
	    get: function(dataObj){
	        // summary:
	        //         Appends the entered field data as a property
	        //         of the passed object and returns the object.
	        // description:
            //         Appends the entered field data as a property
            //         of the passed object and returns the object.
	        //         This interface is written to ensure that container
	        //         fields have the ability to add the value of their
	        //         children; by simply appending more properties.
	        // dataObj: object
	        //         Object to append the data to.
	        if ((typeof this.object != null) && (dataObj[this.name] == undefined)){
	            dataObj[this.name] = this.object.value
	        }
	        else{
	            console.log("DataCrash? ^^");
	        }
	        return dataObj 
	    },
	    set: function(value){
	        // summary:
	        //         Sets the value of the form field.
	        // description:
	        //         Sets the value of the form field.
	        //         Funny enough this interface is not prepared for running
	        //         container objects This has to be updated.
	        //         Only works if field is rendered.
	        // value: string
	        //         value to give to the field
	        
	        /* TODO: Update this interface to support container fields */
            if (typeof this.object != null){
                this.object.value = value;
            }	        
	    }
    }
)

dojo.declare("sfdr.form.txtfield", sfdr.form.field, {
		type: "text"
		// summary:
	    //         Text field
        // name: string
        //         Name of the field
        // title: string
        //         Human readable name of field (usually used as field label)
        // placeholder: string
        //         Input placeholder, text that remains within the input fields
        //         before the user fills them out.
    }
)

dojo.declare("sfdr.form.cxbx", sfdr.form.field, {
        type: "checkbox",
        constructor: function(name, title){
            // summary:
            //         checkbox
            // name: string
            //         Name of the checkbox
            // title: string
            //         Human readable name of checkbox (usually used as field label)
            this.name = name;
            this.title = title;
        },
        get: function(dataObj){
            // summary:
            //         Appends the checked status as a property to the
            //         passed object and returns the object.
            // description:
            //         Appends the checked status as a property to the
            //         passed object and returns the object.
            //         This interface is written to ensure that container
            //         fields have the ability to add the value of their
            //         children; by simply appending more properties.
            // dataObj: object
            //         Object to append the data to.
            if ((typeof this.object != null) && (dataObj[this.name] == undefined)){
                dataObj[this.name] = this.object.checked;
            }
            else{
                console.log("DataCrash? ^^");
            }
            return dataObj 
        },
        set: function(val){
            // summary:
            //         Checks or unchecks the checkbox.
            // description:
            //         Checks or unchecks the checkbox.
            //         Funny enough this interface is not prepared for running
            //         container objects This has to be updated.
            //         Only works if field is rendered.
            // value: boolean
            //         value to give to the checkbox            
            if (typeof this.object != null){
                this.object.checked = val;
            }     
        }
    }
)

dojo.declare("sfdr.form.selectfield", sfdr.form.field, {
		options: null,
	    constructor: function(name, title, options){
	        // summary:
	        //         Select field
	        // name: string
	        //         Name of the field
	        // title: string
	        //         Human readable name of field (used as label)
	        // options: list
	        //         List of objects representing options for the field.
	        //         Objects have the following properties: 
	        //         "val": option value
	        //         "txt": text for user to see (label)
	    	this.name = name;
	    	this.title = title;
	    	this.options = options;
	    },
		render: function(parent){
		    // summary:
		    //        Renders the field into DOM
		    // parent:
		    //        The parent DOM node of this field
	    	this.wrapper = dojo.create("li", null, parent);
	    	dojo.create("span", {innerHTML:this.title}, this.wrapper);
	    	this.object = dojo.create("select", {name:this.name}, this.wrapper);
			for (o in this.options){
				dojo.create("option", {innerHTML: this.options[o].txt, value: this.options[o].val}, this.object)
			}
		}
    }
)

dojo.declare("sfdr.form.listfield", sfdr.form.field, {
	    fields: {},
	    items: [],
	    tbl: null,
	    df: [],
	    form: null,
		addfield: function(field){
		    // summary:
		    //        adds a field to the list
		    // field:
		    //        field object to add
		    this.fields[field.name] = field;
		},
        constructor: function(title, name){
            // summary:
            //        List field
            // description:
            //        List field; in itself a form, that populates a list
            //        or a table of values.
            //        List fields currently support adding and removing items.
            //        Support for editing and reordering items are planned.
            // title:
            //        Human readable name, used as label or heading.
            // name:
            //        field name
            this.title = title;
            this.name = name;
        },
        render: function(parent){
            // summary: 
            //        renders the field into DOM
            // parent:
            //        parent DOM node
            var parent = dojo.create("div", {innerHTML:"<h2>"+this.title+"</h2>"}, parent);
            this.form = dojo.create("form", null, parent);
            var ul = dojo.create("ul", null, this.form);
            var button = dojo.create("input", {type:"button", value: "add"}, this.form);
            this.tbl = dojo.create("table", null, parent);
            tr = dojo.create("tr", null, this.tbl);
            for (f in this.fields){
                if (f != "__proto__"){
                    this.fields[f].render(ul);
                    dojo.create("th",{innerHTML: this.fields[f].title }, tr);                    
                }
            };
            dojo.connect(button, "onclick", this, this.add);
            dojo.create("th", {innerHTML: "Delete"}, tr);
        },
        get: function(dataObj){
            // summary:
            //        Appends the checked status as a property to the
            //        passed object and returns the object.
            // description:
            //        Appends the checked status as a property to the
            //        passed object and returns the object.
            //        This interface is written to ensure that container
            //        fields have the ability to add the value of their
            //        children; by simply appending more properties.
            // dataObj: object
            //        Object to append the data to.
            if (dataObj[this.name] == undefined){
                dataObj[this.name] = this.items;
            }
            else{
                console.log("DataCrash? ^^");
            }
            return dataObj;
        },
        add: function(){
            // summary:
            //        Reads the form, adds the item to the list, resets form.
            d = {};
            for (f in this.fields){
                d = this.fields[f].get(d);
            }
            var next = this.items.length;
            this.items[next] = d;

            this.rowadd(d, next);
            this.form.reset();
        },
        del: function(){
            // summary:
            //        Deletes the item from the list
            // description:
            //        Deletes an item from the list, bound so that
            //        "this" is the df of the item to delete
            dojo.destroy(this.r);
            delete this.p.items[this.i];
            delete this.p.df[this.i];
        },
        rowadd: function(val, i){
            // summary:
            //        Adds an item to the table in the DOM structure
            // val: object
            //        An object representing all the values the item has.
            // i: integer
            //        index for manipulation
            var row = dojo.create("tr", null, this.tbl);
            for (f in this.fields){
                dojo.create("td", {innerHTML: val[f]}, row);                
            }
            var b = dojo.create("input", {type:"button", value:"delete"}, dojo.create("td", null, row))
            this.df[i] = {r:row,p:this,i:i};
            dojo.connect(b, "onclick", this.df[i], this.del);
        },
        set: function(val){
            // summary:
            //         Populates the list
            // val: list
            //         list of objects representing rows   
            this.items = val
            for(v in this.items){
                this.rowadd(this.items[v], v);
            }
        }
    }	
)

dojo.declare("sfdr.form.form", null, {
    fields: {},
    lists: {},
    container: null,
    ul: null,
    constructor: function(cfg, container){
        // summary:
        //        Container object for forms
        // description:
        //        Container object for forms,
        //        The object can render the form and submit it.
        //        the constructor uses supplied config to construct the form
        // cfg:
        //        Form configuration
        // container:
        //        Parent DOM object
        this.container = container;
        for (f in cfg){
            switch(cfg[f].type){
            case "text":
                this.fields[cfg[f].name] = sfdr.form.txtfield(cfg[f].name, cfg[f].title, cfg[f].ph);
                break;
            case "select":
                this.fields[cfg[f].name] = sfdr.form.selectfield(cfg[f].name, cfg[f].title, cfg[f].opt);
                break;
            case "cxbx":
                this.fields[cfg[f].name] = sfdr.form.cxbx(cfg[f].name, cfg[f].title);
                break;
            case "list":
                var l = sfdr.form.listfield(cfg[f].title, cfg[f].name);
                for (g in cfg[f].fields){
                    l.addfield(sfdr.form.txtfield(cfg[f].fields[g].name, cfg[f].fields[g].title, cfg[f].fields[g].ph));
                }
                this.lists[cfg[f].name] = l;
                break;
            }
        }
    },
    render: function(){
        // summary:
        //        renders the form into DOM.
        this.ul = dojo.create("ul", null, this.container);
        for (f in this.fields){
            this.fields[f].render(this.ul);
        }
        dojo.connect(dojo.create("input", {type: "button", value: "send"}, dojo.create("li", null, this.ul)), "onclick", this, this.send);
        for (l in this.lists){
            this.lists[l].render(this.container)
        }
    },
    send: function(){
        // summary:
        //        Reads the form, wraps up the data and sends it to the server.
        var d = {type: mod};
        for (f in this.fields){
            d = this.fields[f].get(d);
        }
        for (l in this.lists){
            d = this.lists[l].get(d);
        }
        dojo.xhrPost({
          url: "/ajax/feed/"+feed+"/cf/store.json",
          timeout: 2000,
          content: { data: dojo.toJson(d) },
          load: function(result){alert("Done");}
        });
    },
    set: function(values){
        // summary:
        //        sets the values of the form
        for (v in values){
            if (this.fields[v] != undefined){
                this.fields[v].set(values[v]);
            } else if (this.lists[v] != undefined){
                this.lists[v].set(values[v]);
            }
        }
    }
})
