import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CemeteryMap } from './cemetery-map';

describe('CemeteryMap', () => {
  let component: CemeteryMap;
  let fixture: ComponentFixture<CemeteryMap>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CemeteryMap],
    }).compileComponents();

    fixture = TestBed.createComponent(CemeteryMap);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
