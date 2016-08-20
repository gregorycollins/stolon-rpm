%global commit      b240c37889bc087ea6751bad22c49debdd3d243d
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%define debug_package %{nil}
%define go_path %{_builddir}/go
%define go_package github.com/sorintlab/stolon
%define go_package_src %{go_path}/src/%{go_package}

Name:           stolon
Version:        0.2.0.%{shortcommit}
Release:        1%{?dist}
Summary:        PostgreSQL cloud native High Availability

Group:          System Environment/Daemons
License:        APLv2.0
URL:            https://github.com/sorintlab/stolon
Source0:        https://github.com/sorintlab/stolon/archive/%{commit}.tar.gz
Source1:        stolon-keeper.service
Source2:        stolon-keeper.sysconfig
Source3:        stolon-proxy.service
Source4:        stolon-proxy.sysconfig
Source5:        stolon-sentinel.service
Source6:        stolon-sentinel.sysconfig
Source7:        cluster-config.json

BuildRequires: golang git
BuildRequires: bash gcc-c++
BuildRequires: systemd-units

Requires(pre): shadow-utils
Requires:      systemd glibc

%package keeper
Summary: stolon keeper
Requires: stolon = %{version}

%package proxy
Summary: stolon proxy
Requires: stolon = %{version}

%package sentinel
Summary: stolon sentinel
Requires: stolon = %{version}

%description
stolon is a cloud native PostgreSQL manager for PostgreSQL high availability.
It's cloud native because it'll let you keep an high available PostgreSQL inside
your containers (kubernetes integration) but also on every other kind of
infrastructure (cloud IaaS, old style infrastructures etc...)

%description keeper
Keeper manages a PostgreSQL instance converging to the clusterview provided by the sentinel(s).

%description proxy
Proxy is the client's access point. It enforce connections to the right PostgreSQL master and forcibly closes connections to unelected masters.

%description sentinel
Sentinel discovers and monitors keepers and calculates the optimal clusterview

%prep
%autosetup -n %{name}-%{commit}
mkdir -p %{go_package_src}
cp -R * %{go_package_src}/.

%build
export GOPATH=%{go_path}
cd %{go_package_src}
bash build

%install
mkdir -p %{buildroot}/%{_bindir}
install %{go_package_src}/bin/stolonctl %{buildroot}/%{_bindir}

# keeper
install %{go_package_src}/bin/stolon-keeper %{buildroot}/%{_bindir}
install -D %{SOURCE1} %{buildroot}/%{_unitdir}/%{name}-keeper.service
install -D %{SOURCE2} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}-keeper

# proxy
install %{go_package_src}/bin/stolon-proxy %{buildroot}/%{_bindir}
install -D %{SOURCE3} %{buildroot}/%{_unitdir}/%{name}-proxy.service
install -D %{SOURCE4} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}-proxy

# sentinel
install %{go_package_src}/bin/stolon-sentinel %{buildroot}/%{_bindir}
install -D %{SOURCE5} %{buildroot}/%{_unitdir}/%{name}-sentinel.service
install -D %{SOURCE6} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}-sentinel
install -D %{SOURCE7} %{buildroot}/%{_sysconfdir}/%{name}/cluster-config.json

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -s /sbin/nologin \
    -c "stolon user" %{name}
exit 0

%postun
userdel %{name} && groupdel %{name}

%post keeper
%systemd_post %{name}-keeper.service

%preun keeper
%systemd_preun %{name}-keeper.service

%postun keeper
%systemd_postun_with_restart %{name}-keeper.service

%post proxy
%systemd_post %{name}-proxy.service

%postun proxy
%systemd_postun_with_restart %{name}-proxy.service

%preun proxy
%systemd_preun %{name}-proxy.service

%post sentinel
%systemd_po-st %{name}-sentinel.service

%preun sentinel
%systemd_preun %{name}-sentinel.service

%postun sentinel
%systemd_postun_with_restart %{name}-sentinel.service

%clean
rm -rf %{go_package_src}
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%attr(755, root, root) %{_bindir}/stolonctl

%files keeper
%defattr(-,root,root,-)
%attr(755, root, root) %{_bindir}/stolon-keeper
%attr(644, root, root) %{_unitdir}/%{name}-keeper.service
%config(noreplace) %attr(640, root, %{name}) %{_sysconfdir}/sysconfig/%{name}-keeper

%files proxy
%defattr(-,root,root,-)
%attr(755, root, root) %{_bindir}/stolon-proxy
%attr(644, root, root) %{_unitdir}/%{name}-proxy.service
%config(noreplace) %attr(640, root, %{name}) %{_sysconfdir}/sysconfig/%{name}-proxy

%files sentinel
%defattr(-,root,root,-)
%attr(755, root, root) %{_bindir}/stolon-sentinel
%attr(644, root, root) %{_unitdir}/%{name}-sentinel.service
%config(noreplace) %attr(640, root, %{name}) %{_sysconfdir}/sysconfig/%{name}-sentinel
%dir %attr(750, root, %{name}) %{_sysconfdir}/%{name}
%attr(640, root, %{name}) %{_sysconfdir}/%{name}/cluster-config.json

%doc

%changelog
* Sat Aug 20 2016 Arun Babu Neelicattu <arun.neelicattu@gmail.com> - 0.2.0.b240c37-1
- intial version from master post 0.2.0 release

