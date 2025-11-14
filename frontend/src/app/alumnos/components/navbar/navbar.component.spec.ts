import { AuthService } from "@/auth/services/auth.service";
import { provideHttpClientTesting } from "@angular/common/http/testing";
import { ComponentFixture, TestBed } from "@angular/core/testing";
import { Router, provideRouter } from "@angular/router";
import { NavbarComponent } from "./navbar.component";
import { provideHttpClient } from "@angular/common/http";
import { signal } from "@angular/core";
import { of } from "rxjs";
import { AlumnoStateService } from "@/alumnos/services/alumno-state.service";

class AuthServiceMock {
  checkAdmin = jasmine.createSpy('checkAdmin').and.callFake(() => {
    return of(true);
  });
}

class AlumnoStateServiceMock {
  getId = jasmine.createSpy('getId').and.callFake(() => {
    return "42";
  });
}

describe('NavbarComponent', () => {

  let fixture: ComponentFixture<NavbarComponent>;
  let component: NavbarComponent;
  let authService: AuthService;
  let alumnoStateService: AlumnoStateService;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NavbarComponent],
      providers: [
        { provide: AuthService, useClass: AuthServiceMock },
        { provide: AlumnoStateService, useClass: AlumnoStateServiceMock },
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([
        ]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(NavbarComponent);
    authService = TestBed.inject(AuthService);
    alumnoStateService = TestBed.inject(AlumnoStateService);
    router = TestBed.inject(Router);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should toggle mobile menu', () => {
    expect(component.mobileMenuOpen()).toBeFalse();
    component.toggleMobileMenu();
    expect(component.mobileMenuOpen()).toBeTrue();
    component.toggleMobileMenu();
    expect(component.mobileMenuOpen()).toBeFalse();
  });

  it('should close mobile menu', () => {
    component.mobileMenuOpen.set(true);
    component.closeMobileMenu();
    expect(component.mobileMenuOpen()).toBeFalse();
  });

  it('should navigate to alumno page', async () => {
    spyOn(router, 'navigate');
    component.goToAlumnoPage();
    expect(alumnoStateService.getId).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['alumno/42']);
  });

  it('should navigate to alumno page with null id when there is no id', async () => {
    spyOn(router, 'navigate');
    (alumnoStateService.getId as jasmine.Spy).and.returnValue(null);
    component.goToAlumnoPage();
    expect(alumnoStateService.getId).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/alumno']);
  });

  it('should navigate to admin login', async () => {
    spyOn(router, 'navigate');
    component.goToAdminLogin();
    expect(authService.checkAdmin).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/admin/login']);
  });
});
