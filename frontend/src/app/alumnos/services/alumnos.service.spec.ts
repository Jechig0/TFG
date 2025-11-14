import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient } from "@angular/common/http";
import { CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA } from "@angular/core";
import { TestBed } from "@angular/core/testing";
import { provideRouter } from "@angular/router";
import { AlumnosService } from "./alumnos.service";
import { environment } from '@environments/environment';
import { AlumnoStateService } from './alumno-state.service';

class AlumnoStateServiceMock {
  clear = jasmine.createSpy('clear').and.callFake(() => {

  });
}

describe('AlumnosService', () => {

  let service: AlumnosService;
  let httpMock: HttpTestingController;
  let alumnoStateService: AlumnoStateService


  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        AlumnosService,
        { provide: AlumnoStateService, useClass: AlumnoStateServiceMock }
      ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
    }).compileComponents();
  });

  beforeEach(() => {
    service = TestBed.inject(AlumnosService);
    httpMock = TestBed.inject(HttpTestingController);
    alumnoStateService = TestBed.inject(AlumnoStateService)
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('getAlumnoById should fetch alumno', () => {
    const dummyData: [string, number][] = [['Matemáticas', 8], ['Física', 7]];

    service.getAlumnoById('1').subscribe(data => {
      expect(data).toEqual(dummyData);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/alumno/1`);
    expect(req.request.method).toBe('GET');
    req.flush(dummyData);
  });

  it('getMediaAlumno should fetch media', () => {
    const dummyMedia = '7.5';
    service.getMediaAlumno('1').subscribe(data => {
      expect(data).toBe(dummyMedia);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/alumno/1/media/`);
    expect(req.request.method).toBe('GET');
    req.flush(dummyMedia);
  });

  it('verificarAlumno should post id and dni', () => {
    const dummyResponse = { estado: 'OK' };
    service.verificarAlumno('1', '12345678A').subscribe(data => {
      expect(data).toBe('OK');
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/alumno/verificar`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ id_alumno: '1', dni: '12345678A' });
    req.flush(dummyResponse);
  });

  it('getAsignaturas should fetch asignaturas', () => {
    const dummy = [['Matemáticas'], ['Física']];
    service.getAsignaturas('1').subscribe(data => {
      expect(data).toEqual(dummy);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/asignatura/1`);
    expect(req.request.method).toBe('GET');
    req.flush(dummy);
  });

  it('getProbabilidadAcceso should fetch number', () => {
    service.getProbabilidadAcceso('1', 'Matemáticas').subscribe(data => {
      expect(data).toBe(0.9);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/alumno/probabilidadEntrada/1/Matemáticas`);
    expect(req.request.method).toBe('GET');
    req.flush(0.9);
  });

  it('getAfinidadAsignatura should fetch number', () => {
    service.getAfinidadAsignatura('1', 'Física').subscribe(data => {
      expect(data).toBe(0.7);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/alumno/afinidad/1/Física`);
    expect(req.request.method).toBe('GET');
    req.flush(0.7);
  });

  it('enviarInformePdf should post FormData', () => {
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
    const dummy: any[] = [{ asignatura: 'Matemáticas', nota: 8 }];

    service.enviarInformePdf('1', '12345678A', file).subscribe(data => {
      expect(data).toEqual(dummy);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/alumno/1/subir-informe`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body.has('file')).toBeTrue();
    expect(req.request.body.get('dni')).toBe('12345678A');
    req.flush(dummy);
  });

  it('eliminarAlumno should call clear and delete', () => {
    const dummy = { estado: 'OK' };

    service.eliminarAlumno('1').subscribe(data => {
      expect(data).toEqual(dummy);
    });

    expect(alumnoStateService.clear).toHaveBeenCalled();

    const req = httpMock.expectOne(`${environment.apiUrl}/alumno/delete/1`);
    expect(req.request.method).toBe('DELETE');
    req.flush(dummy);
  });


});
