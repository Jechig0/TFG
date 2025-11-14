import { provideHttpClient } from "@angular/common/http";
import { HttpTestingController, provideHttpClientTesting } from "@angular/common/http/testing";
import { CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA } from "@angular/core";
import { TestBed } from "@angular/core/testing";
import { provideRouter } from "@angular/router";
import { AlumnoStateService } from "./alumno-state.service";
import { sha256 } from 'js-sha256';



describe('AlumnoStateService', () => {

  let service: AlumnoStateService;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        AlumnoStateService,
      ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
    }).compileComponents();
  });

  beforeEach(() => {
    service = TestBed.inject(AlumnoStateService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('setAlumno should store id and hashed dni in sessionStorage', () => {
    const id = '123';
    const dni = '12345678A';

    service.setAlumno(id, dni);

    expect(sessionStorage.getItem('id_alumno')).toBe(id);
    expect(sessionStorage.getItem('dni')).toBe(sha256(dni.toUpperCase().trim()));
    expect(sessionStorage.getItem('isAdmin')).toBe('false');
  });

  it('getId should retrieve id from sessionStorage', () => {
    const id = '123';
    sessionStorage.setItem('id_alumno', id);
    expect(service.getId()).toBe(id);
  });

  it('getDni should retrieve hashed dni from sessionStorage', () => {
    const dni = '12345678A';
    const hashedDni = sha256(dni.toUpperCase().trim());
    sessionStorage.setItem('dni', hashedDni);
    expect(service.getDni()).toBe(hashedDni);
  });

  it('clear should remove id, dni, and isAdmin from sessionStorage', () => {
    sessionStorage.setItem('id_alumno', '123');
    sessionStorage.setItem('dni', 'hashedDni');
    sessionStorage.setItem('isAdmin', 'false');

    service.clear();

    expect(sessionStorage.getItem('id_alumno')).toBeNull();
    expect(sessionStorage.getItem('dni')).toBeNull();
    expect(sessionStorage.getItem('isAdmin')).toBeNull();
  });
});
