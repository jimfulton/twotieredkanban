// HTML5-based Drag and Drop supprt

import React from 'react';
import classes from 'classnames';

class Draggable extends React.Component {

  constructor(props) {
    super(props);
    this.state = {class_name: ''};
  }

  render() {

    const dragstart = (ev) => {
      if (! ev.dataTransfer.types.length) {
        const data = this.props.data;
        for (const name in data) {
          ev.dataTransfer.setData(name, data[name]);
        }
      }
      this.setState({class_name: 'dragging'});
    };
    const dragend   = () => this.setState({class_name: ''});
    
    return (
      <div draggable="true"
           className={this.state.class_name}
           onDragStart={dragstart}
           onDragEnd={dragend}
           >
        {this.props.children}
      </div>
    );
  }
}

class DropZone extends React.Component {
  
  constructor(props) {
    super(props);
    this.state = {dragover: false};
  }

  allowed(dt) {
    return this.props.disallow.filter(
      (t) => dt.types.indexOf('text/' + t) >= 0).length == 0;
  }
  
  dragover(ev) {
    if (this.allowed(ev.dataTransfer)) {
      ev.preventDefault();
      return false;
    }
    else {
      return true;
    };
  }

  dragenter(ev) {
    if (this.allowed(ev.dataTransfer)) {
      this.setState({dragover: true});
    }
  }

  dragleave() {
    this.setState({dragover: false});
  }

  drop(ev) {
    ev.preventDefault();
    this.dragleave();
    this.props.dropped(ev.dataTransfer);
  }

  
  render() {

    const className = classes(
      this.props.className,
      {dragover: this.state.dragover});
    
    return (
      <div className={className}
           onDragEnter={(ev) => this.dragenter(ev)}
           onDragLeave={(ev) => this.dragleave(ev)}
           onDragOver={(ev) => this.dragover(ev)}
           onDrop={(ev) => this.drop(ev)}
           >
        {this.props.children}
      </div>
    );
  }
}

DropZone.defaultProps = {disallow: []};


module.exports = {
  Draggable: Draggable,
  DropZone: DropZone
};
