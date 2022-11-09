# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
%define debug_package %{nil}
%define __jar_repack %{nil}

%define impala_name impala
%define usr_lib_impala %{parent_dir}/usr/lib/%{impala_name}
%define var_lib_impala %{parent_dir}/var/lib/%{impala_name}

%define doc_dir %{parent_dir}/%{_docdir}

# No prefix directory
%define np_var_run_impala /var/run/%{impala_name}

Name:       %{impala_name}
Version:    %{impala_base_version}
Release:    %{impala_release}
Summary:    massively parallel processing query engine
License:    Apache 2.0
URL:        http://impala.apache.org/
Group:      Applications/Internet
BuildRoot:  %{_topdir}/INSTALL/%{impala_name}-%{version}
Source0:    apache-%{impala_name}-%{impala_base_version}.tar.gz
Source1:    do-component-build

Requires: bigtop-utils >= 0.7

AutoReqProv: no

%description
Impala is an open source massively parallel processing query engine on top of clustered systems like Apache Hadoop

%package        shell
Summary:        impala shell files
Group:          Applications/Internet
Requires: python

%description    shell
impala shell files

%package        catalog
Summary:        impala catalog daemon script
Group:          Applications/Internet

%description    catalog
impala catalog daemon script

%package        server
Summary:        impala server daemon script
Group:          Applications/Internet

%description    server
impala server daemon script

%package        state-store
Summary:        impala state-store daemon script
Group:          Applications/Internet

%description    state-store
impala state-store daemon script

%prep
%setup -q -n apache-%{impala_name}-%{impala_base_version}

%build
bash %{SOURCE1}

%clean
%{__rm} -rf %{buildroot}

#########################
#### INSTALL SECTION ####
#########################
%install
%{__rm} -rf %{buildroot}
%{__install} -d %{buildroot}
%{__install} -d %{buildroot}/etc/impala/conf
%{__install} -d %{buildroot}/usr/bin
%{__install} -d %{buildroot}/usr/lib/impala
%{__install} -d %{buildroot}/var/lib/impala
%{__install} -d %{buildroot}/var/log/impala
%{__install} -d %{buildroot}/var/run/impala

%{__install} -d %{buildroot}/usr/lib/impala/lib
%{__cp} -rp fe/target/dependency/* %{buildroot}/usr/lib/impala/lib/
%{__cp} -p fe/target/impala-frontend-%{impala_base_version}-RELEASE.jar %{buildroot}/usr/lib/impala/lib/
%{__cp} -rp www %{buildroot}/usr/lib/impala/

%{__install} -d %{buildroot}/usr/lib/impala/toolchain
%{__cp} -rp toolchain/toolchain-packages-gcc7.5.0/gcc-7.5.0 %{buildroot}/usr/lib/impala/toolchain
%{__cp} -rp toolchain/toolchain-packages-gcc7.5.0/kudu-1.16.0 %{buildroot}/usr/lib/impala/toolchain

%{__install} -d %{buildroot}/usr/lib/impala-shell
%{__cp} -rp shell/build/impala-shell-%{impala_base_version}-RELEASE/ext-py %{buildroot}/usr/lib/impala-shell
%{__cp} -rp shell/build/impala-shell-%{impala_base_version}-RELEASE/gen-py %{buildroot}/usr/lib/impala-shell
%{__cp} -rp shell/build/impala-shell-%{impala_base_version}-RELEASE/lib %{buildroot}/usr/lib/impala-shell
%{__cp} -r shell/build/impala-shell-%{impala_base_version}-RELEASE/impala_shell.py %{buildroot}/usr/lib/impala-shell
%{__cp} -r shell/build/impala-shell-%{impala_base_version}-RELEASE/impala-shell %{buildroot}/usr/bin/

%{__install} -d %{buildroot}/etc/security/limits.d
%{__cp} -rp $RPM_SOURCE_DIR/limits.d/impala.conf %{buildroot}/etc/security/limits.d/

%{__install} -d %{buildroot}/etc/default
%{__cp} -p $RPM_SOURCE_DIR/default/* %{buildroot}/etc/default/

%{__install} -d %{buildroot}/etc/rc.d/init.d/
%{__cp} -rp $RPM_SOURCE_DIR/init.d/* %{buildroot}/etc/rc.d/init.d/
%{__chmod} +755 %{buildroot}/etc/rc.d/init.d/*

%{__cp} -rp $RPM_SOURCE_DIR/bin/* %{buildroot}/usr/bin
%{__chmod} +755 %{buildroot}/usr/bin/*

%{__cp} -rp $RPM_SOURCE_DIR/conf/* %{buildroot}/etc/impala/conf

%{__install} -d %{buildroot}/usr/lib/impala/sbin
%{__cp} -p be/build/latest/service/libfesupport.so %{buildroot}/usr/lib/impala/sbin
%{__cp} -p be/build/latest/service/impalad %{buildroot}/usr/lib/impala/sbin
cd %{buildroot}/usr/lib/impala/sbin && ln -s impalad catalogd
cd %{buildroot}/usr/lib/impala/sbin && ln -s impalad statestored

%pre
getent group impala >/dev/null || groupadd -r impala
getent passwd impala >/dev/null || useradd -c "Impala" -s /bin/bash -g impala -m -d %{var_lib_impala} impala 2> /dev/null || :

%post
systemctl daemon-reload

%preun

%postun
systemctl daemon-reload
if [ $1 -eq 0 ]; then
    /usr/sbin/userdel impala || %logmsg "User \"impala\" could not be deleted."
fi

#######################
#### FILES SECTION ####
#######################
%files
%defattr(-,root,root,-)
/etc/security/limits.d/impala.conf
/etc/default
/etc/impala/conf
/usr/bin/catalogd
/usr/bin/impalad
/usr/bin/statestored
/usr/lib/impala

%defattr(-,impala,impala,-)
/var/lib/impala
/var/log/impala
/var/run/impala

%files shell
%defattr(-,root,root,-)
/usr/bin/impala-shell
/usr/lib/impala-shell

%files catalog
%defattr(-,root,root,-)
/etc/rc.d/init.d/impala-catalog

%files server
%defattr(-,root,root,-)
/etc/rc.d/init.d/impala-server

%files state-store
%defattr(-,root,root,-)
/etc/rc.d/init.d/impala-state-store
