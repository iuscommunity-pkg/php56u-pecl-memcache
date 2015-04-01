%global pecl_name memcache
%global real_name php-pecl-memcache
%global ini_name  40-%{pecl_name}.ini
%global php_base php56u

Summary: Extension to work with the Memcached caching daemon
Name: %{php_base}-pecl-memcache
Version: 3.0.8
Release: 3.ius%{?dist}
License: PHP
Group: Development/Languages
Vendor: IUS Community Project
URL: http://pecl.php.net/package/%{pecl_name}

Source: http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
Source2: xml2changelog

BuildRequires: %{php_base}-devel
BuildRequires: %{php_base}-pear
BuildRequires: zlib-devel
Requires(post): %{php_base}-pear
Requires(postun): %{php_base}-pear
Requires: php(zend-abi) = %{php_zend_api}
Requires: php(api) = %{php_core_api}

Provides:     php-pecl(%{pecl_name}) = %{version}
Provides:     php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:     php-%{pecl_name} = %{version}
Provides:     php-%{pecl_name}%{?_isa} = %{version}
Provides:     %{php_base}-pecl(%{pecl_name}) = %{version}
Provides:     %{php_base}-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:     %{php_base}-%{pecl_name} = %{version}
Provides:     %{php_base}-%{pecl_name}%{?_isa} = %{version}
Provides:     %{real_name} = %{version}-%{release}
Conflicts:    %{real_name} < %{version}

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
Memcached is a caching daemon designed especially for
dynamic web applications to decrease database load by
storing objects in memory.

This extension allows you to work with memcached through
handy OO and procedural interfaces.

Memcache can be used as a PHP session handler.


%prep
%setup -c -n %{real_name}-%{version} -q
mv %{pecl_name}-%{version} NTS
%{_bindir}/php %{SOURCE2} package.xml > CHANGELOG

%{__cat} > %{ini_name} << 'EOF'
; ----- Enable %{pecl_name} extension module
extension=%{pecl_name}.so

; ----- Options for the %{pecl_name} module
; see http://www.php.net/manual/en/memcache.ini.php

; Whether to transparently failover to other servers on errors
;memcache.allow_failover=1
; Data will be transferred in chunks of this size
;memcache.chunk_size=32768
; Autocompress large data
;memcache.compress_threshold=20000
; The default TCP port number to use when connecting to the memcached server 
;memcache.default_port=11211
; Hash function {crc32, fnv}
;memcache.hash_function=crc32
; Hash strategy {standard, consistent}
;memcache.hash_strategy=consistent
; Defines how many servers to try when setting and getting data.
;memcache.max_failover_attempts=20
;  The protocol {ascii, binary} : You need a memcached >= 1.3.0 to use the binary protocol
;  The binary protocol results in less traffic and is more efficient
;memcache.protocol=ascii
;  Redundancy : When enabled the client sends requests to N servers in parallel
;memcache.redundancy=1
;memcache.session_redundancy=2
;  Lock Timeout
;memcache.lock_timeout = 15

; ----- Options to use the memcache session handler

; RPM note : save_handler and save_path are defined
; for mod_php, in /etc/httpd/conf.d/php.conf
; for php-fpm, in /etc/php-fpm.d/*conf

; Use memcache as a session handler
;session.save_handler=memcache
; Defines a comma separated of server urls to use for session storage
;session.save_path="tcp://localhost:11211?persistent=1&weight=1&timeout=1&retry_interval=15"
EOF

cp -r NTS ZTS


%build
cd NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
%{__make} %{?_smp_mflags}

cd ../ZTS
%{_bindir}/zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
%{__make} %{?_smp_mflags}


%install
%{__make} -C NTS install INSTALL_ROOT=%{buildroot}
%{__install} -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

%{__make} -C ZTS install INSTALL_ROOT=%{buildroot}
%{__install} -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}

# Install XML package description
%{__install} -Dpm 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Test & Documentation
for i in $(grep 'role="test"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do %{__install} -Dpm 644 NTS/$i %{buildroot}%{pecl_testdir}/%{pecl_name}/$i
done
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do %{__install} -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done
%{__install} -Dpm 644 CHANGELOG %{buildroot}%{pecl_docdir}/%{pecl_name}/CHANGELOG


%check
: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    -m | grep %{pecl_name}

: Minimal load test for ZTS extension
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    -m | grep %{pecl_name}


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ]; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%doc %{pecl_docdir}/%{pecl_name}
%doc %{pecl_testdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so



%changelog
* Wed Apr 01 2015 Ben Harper <ben.harper@rackspace.com> - 3.0.8-4.ius
- porting from php55u-pecl-memcache

* Thu Oct 09 2014 Carl George <carl.george@rackspace.com> - 3.0.8-3.ius
- Sync with Fedora package
- Clean up requires/buildrequires/provides
- Add numerical prefix to extension configuration file
- Install doc in pecl_docdir
- Install tests in pecl_testdir
- Enable ZTS build
- Add filter_provides to avoid private-shared-object-provides memcache.so
- Add minimal load test in %%check

* Mon Jan  6 2014 Mark McKinstry <mmckinst@nexcess.net> - 0:3.0.8-2.ius
- modify php54 spec for php55u
- take out -n flag when running xml2changelog since we need to load php.ini to
  get simplexml support

* Mon Apr 08 2013 Ben Harper <ben.harper@rackspace.com> - 0:3.0.8-1.ius
- Latest sources from upstream. Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=3.0.8

* Thu Nov 01 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.7-2.ius
- Rebuilding against internal 6.3.z

* Mon Sep 24 2012 Ben Harper <ben.harper@rackspace.com> - 0:3.0.7.ius
- Latest sources from upstream. Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=3.0.7

* Tue Aug 21 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.6-5.ius
- Rebuilding against php54-5.4.6-2.ius as it is now using bundled PCRE.

* Fri May 11 2012 Dustin Henry Offutt <dustin.offutt@rackspace.com> - 0:3.0.6-4.ius
- Building for PHP54

* Fri Aug 19 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.6-3.ius
- Rebuilding

* Fri Aug 12 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.6-2.ius
- Rebuilding with EL6 support

* Mon Apr 11 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.6-1.ius
- Latest sources from upstream. Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=3.0.6

* Fri Feb 11 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.0.5-1.ius
- Latest sources from upstream. Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=3.0.5
- Changed basever from 2.2 to 3

* Thu Feb 03 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:2.2.6-2.ius
- Removed Obsoletes: php53*

* Thu Dec 16 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:2.2.6-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=2.2.6
- Rename package as php53u-pecl-memcache. Resolves LP#691755
- Rebuild against php53u-5.3.4
- BuildRequires: php53u-cli 

* Mon Jul 27 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:2.2.5-2.ius
- Rebuild for php 5.3.3

* Tue Jun 22 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:2.2.5-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=memcache&release=2.2.5

* Fri Oct 16 2009 BJ Dierkes <wdierkes@rackspace.com> - 0.2.2.3-5.ius
- Repackaging for php53

* Wed Oct 14 2009 BJ Dierkes <wdierkes@rackspace.com> - 0:2.2.3-4.ius
- Repackaging for IUS
- Renaming to php52-pecl-memcache
- Removing Epoch version

* Mon Sep 28 2009 BJ Dierkes <wdierkes@rackspace.com> - 1:2.2.3-3.3.rs
- Rebuilding against new php.

* Mon Sep 14 2009 BJ Dierkes <wdierkes@rackspace.com> - 1:2.2.3-3.2.rs
- Upping Epoch version due to conflicts with EPEL pecl packages.

* Thu Jul 02 2009 BJ Dierkes <wdierkes@rackspace.com> - 2.2.3-3.1.rs
- Rebuild against php-5.2.10
 
* Thu May 07 2009 BJ Dierkes <wdierkes@rackspace.com> - 2.2.3-3.rs
- Rebuild against latest PHP.
    
* Fri Jan 23 2009 BJ Dierkes <wdierkes@rackspace.com> - 2.2.3-2.rs
- Fixing post/postun scripts to properly register with pecl.  Resolves
  Rackspace Bug [#1096].
- Adding php_ver_tag for different major PHP versions.
- Adding Vendor tag.

* Tue Jan 06 2009 BJ Dierkes <wdierkes@rackspace.com> - 2.2.3-1.1.rs
- Rebuild

* Sat Feb  9 2008 Remi Collet <Fedora@FamilleCollet.com> 2.2.3-1
- new version

* Thu Jan 10 2008 Remi Collet <Fedora@FamilleCollet.com> 2.2.2-1
- new version

* Thu Nov 01 2007 Remi Collet <Fedora@FamilleCollet.com> 2.2.1-1
- new version

* Sat Sep 22 2007 Remi Collet <Fedora@FamilleCollet.com> 2.2.0-1
- new version
- add new INI directives (hash_strategy + hash_function) to config
- add BR on php-devel >= 4.3.11 

* Mon Aug 20 2007 Remi Collet <Fedora@FamilleCollet.com> 2.1.2-1
- initial RPM

