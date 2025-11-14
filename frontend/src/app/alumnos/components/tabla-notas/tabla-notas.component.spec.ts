import { createComponent } from "@angular/core";
import { TestBed } from "@angular/core/testing";
import { TablaNotasComponent } from "./tabla-notas.component";

describe('TablaNotasComponent', () => {

  it('should create the component', () => {
    const fixture = TestBed.createComponent(TablaNotasComponent);
    const component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });
});
