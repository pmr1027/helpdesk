var document = this;
var window = this;
(function() {
  this.Modal = function() {
    // Element References
    this.closeBtn = null;
    this.modal = null;
    this.overlay = null;

    // Transition  Prefix
    this.transitionEnd = transitionSelect();

    // Default Options
    var defaults = {
      autoOpen: false,
      className: 'fade-and-drop',
      closeButton: true,
      content: "",
      title: "Modal",
      maxWidth: 600,
      minWidth: 280,
      overlay: true
    };

    // Create options by extending defaults with the passed in arugments
    if (arguments[0] && typeof arguments[0] === "object") {
      this.options = extendDefaults(defaults, arguments[0]);
    }

    if (this.options.autoOpen === true) this.open();
  };

  // Public Methods

  this.Modal.prototype.close = function() {
    var _ = this;
    this.modal.className = this.modal.className.replace(" modal-open", "");
    this.overlay.className = this.overlay.className.replace(" modal-open",
      "");
    this.modal.addEventListener(this.transitionEnd, function() {
      _.modal.parentNode.removeChild(_.modal);
    });
    this.overlay.addEventListener(this.transitionEnd, function() {
      if (_.overlay.parentNode) _.overlay.parentNode.removeChild(_.overlay);
    });
  };
    
  this.Modal.prototype.open = function() {
    buildOut.call(this);
    initializeEvents.call(this);
    window.getComputedStyle(this.modal).height;
    this.modal.className = this.modal.className +
      (this.modal.offsetHeight > window.innerHeight ?
        " modal-open modal-anchored" : " modal-open");
    this.overlay.className = this.overlay.className + " modal-open";
  };

  this.Modal.prototype.content = function(html) {
      this.options.content = html;
  };
  
  this.Modal.prototype.title = function(text) {
      this.options.title = text;
  };
    
  function buildOut() {
    // References
    var content;
    var contentHolder;
    var docFrag;

    /*
     * If content is an HTML string, append the HTML string.
     * If content is a domNode, append its content.
     */

    if (typeof this.options.content === "string") {
      content = this.options.content;
    } else {
      content = this.options.content.innerHTML;
    }

    // Create a DocumentFragment to build with
    docFrag = document.createDocumentFragment();

    // Create modal element
    this.modal = document.createElement("div");
    this.modal.className = "modal " + this.options.className;
    this.modal.style.minWidth = this.options.minWidth + "px";
    this.modal.style.maxWidth = this.options.maxWidth + "px";


    // If overlay is true, add one
    if (this.options.overlay === true) {
      this.overlay = document.createElement("div");
      this.overlay.className = "modal-overlay " + this.options.className;
      docFrag.appendChild(this.overlay);
    }
    
    // Creater inner wrapper
    this.innerWrapper = document.createElement("section");
    this.innerWrapper.className = "modal-inner";
  
    // Create header area and append to modal
    this.header = document.createElement("header");
    this.header.className = 'modal-header';
    this.header.innerHTML = this.options.title;
    this.innerWrapper.appendChild(this.header);
      
     // If closeButton option is true, add a close button
    if (this.options.closeButton === true) {
      this.closeButton = document.createElement("button");
      this.closeButton.className = "modal-close close-btn";
      this.closeButton.textContent = "x";
      this.header.appendChild(this.closeButton);
    }

    // Create content area and append to modal
    contentHolder = document.createElement("div");
    contentHolder.className = "modal-content";
    contentHolder.innerHTML = content;
    console.log(this.options.content);
    //contentHolder.style.maxHeight = window.innerHeight;
    this.innerWrapper.appendChild(contentHolder);
      
    this.modal.appendChild(this.innerWrapper);
    // Append modal to DocumentFragment
    docFrag.appendChild(this.modal);

    // Append DocumentFragment to body
    document.body.appendChild(docFrag);
  }

  function extendDefaults(source, properties) {
    var property;
    for (property in properties) {
      if (properties.hasOwnProperty(property)) {
        source[property] = properties[property];
      }
    }
    return source;
  }

  function initializeEvents() {
    if (this.closeButton) {
      this.closeButton.addEventListener('click', this.close.bind(this));
    }

    if (this.overlay) {
      this.overlay.addEventListener('click', this.close.bind(this));
    }
  }

  function transitionSelect() {
    var el = document.createElement("div");
    if (el.style.WebkitTransition) return "webkitTransitionEnd";
    if (el.style.OTransition) return "oTransitionEnd";
    return 'transitionend';
  }
})();


